from pathlib import Path
import subprocess, hashlib
import sys
root = Path(sys.argv[1])
def edit(name, replacements):
    p = root/name
    raw = p.read_bytes()
    crlf = b'\r\n' in raw
    text = raw.decode().replace('\r\n','\n')
    for old,new in replacements:
        assert text.count(old) == 1, (name, old, text.count(old))
        text = text.replace(old,new)
    text = text.rstrip('\n')+'\n'
    p.write_bytes(text.replace('\n','\r\n').encode() if crlf else text.encode())
edit('src/Comm/FileInfo.cpp', [
    ('\t\tSaveCacheToFile(*request->GetData());', '\t\tSaveCacheToFile(*request->GetData());\n\t\tModel::get().post<EventType::FileInfoReady>(filepath);')])
block = '\n'.join([
    '\t\t/* Retrieve file info and thumbnails for G-codes and macros, including subfolders. */',
    '\t\tconst std::string_view directory = request->GetDir();',
    '\t\tconst auto isWithin = [directory](std::string_view root)',
    '\t\t{', '\t\t\tif (root.empty())', '\t\t\t{', '\t\t\t\treturn false;', '\t\t\t}',
    "\t\t\twhile (root.size() > 1 && root.back() == '/')", '\t\t\t{',
    '\t\t\t\troot.remove_suffix(1);', '\t\t\t}', '\t\t\treturn directory == root ||',
    "\t\t\t\t   (directory.starts_with(root) && directory.size() > root.size() && directory[root.size()] == '/');",
    '\t\t};',
    '\t\tif (!isWithin(OM::Directories::GetGcodesDirectory()) && !isWithin(OM::Directories::GetMacrosDirectory()))'])
invalidation = '\n'.join([
    '\t\t\t\tif (isWithin(OM::Directories::GetMacrosDirectory()))', '\t\t\t\t{',
    '\t\t\t\t\t// Do not retain a previous image when a macro loses its thumbnail.',
    '\t\t\t\t\tstd::error_code ec;',
    '\t\t\t\t\tstd::filesystem::remove(GetThumbnailPath(item->GetPath(), true), ec);',
    '\t\t\t\t\tstd::filesystem::remove(GetThumbnailPath(item->GetPath(), false), ec);',
    '\t\t\t\t}', '\t\t\t\tFILEINFO_CACHE->QueueFileInfoRequest(item->GetPath());'])
edit('src/Subscribers/FileSubscribers.cpp', [
    ('#include <string>', '#include <filesystem>\n#include <string>\n#include <string_view>\n#include <system_error>'),
    ("\t\t/* We don't care about file info (and thumbnails) for files that aren't in the Gcodes directory */\n\t\tif (request->GetDir().find(OM::Directories::GetGcodesDirectory()) == std::string::npos)", block),
    ('\t\t\t\tFILEINFO_CACHE->QueueFileInfoRequest(item->GetPath());', invalidation)])
event_path = root/'src/UI/Core/EventTypes.h'
event_line = next(l for l in event_path.read_text().splitlines(True) if 'XX(ThumbnailData,' in l)
edit('src/UI/Core/EventTypes.h', [(event_line, event_line.replace('ThumbnailData','FileInfoReady')+event_line)])
helper = '\n'.join([
    '\tvoid FilePresenter::requestSelectedMacroThumbnail(const std::string& filename)', '\t{',
    '\t\tUI_LOCK();', '\t\tif (m_baseFolder != BaseFolder::MACROS || m_clickedItem != filename ||',
    '\t\t\t!getView()->getConfirmModal().isVisible())', '\t\t{', '\t\t\treturn;', '\t\t}',
    '\t\t// Retry after metadata arrives or an already running small thumbnail completes.',
    '\t\tm_macroThumbnailPending = !FILEINFO_CACHE->QueueLargeThumbnailRequest(filename);', '\t}', '', ''])
listener = '\n'.join([
    '\t\tregisterEventListener<EventType::FileInfoReady>(', '\t\t\t[this](const std::string& filename)',
    '\t\t\t{', '\t\t\t\tif (m_baseFolder != BaseFolder::MACROS)', '\t\t\t\t{',
    '\t\t\t\t\treturn;', '\t\t\t\t}', '\t\t\t\tUI_LOCK();', '\t\t\t\tdisplayFiles();',
    '\t\t\t\tif (m_clickedItem == filename && getView()->getConfirmModal().isVisible())', '\t\t\t\t{',
    '\t\t\t\t\tconst auto thumbnail = GetThumbnailPath(filename);',
    '\t\t\t\t\tgetView()->getConfirmModal().setImage(IsThumbnailCached(filename) ? thumbnail.c_str() : nullptr);',
    '\t\t\t\t\trequestSelectedMacroThumbnail(filename);', '\t\t\t\t}', '\t\t\t});'])
edit('src/UI/Screens/File/FilePresenter.cpp', [
    ('\t\tm_view->cancelStartPrint();', '\t\tm_view->cancelStartPrint();\n\t\tm_macroThumbnailPending = false;'),
    ('\t\t\tm_view->confirmRunMacro(getDisplayName(item->GetName(), m_baseFolder));',
     '\t\t\tLOG_INFO("Macro thumbnail support v1: {:s}", m_gcodePath);\n\t\t\tm_view->confirmRunMacro(getDisplayName(item->GetName(), m_baseFolder), GetThumbnailPath(item->GetPath()));\n\t\t\trequestSelectedMacroThumbnail(item->GetPath());'),
    ('\tvoid FilePresenter::newThumbnailData(const std::string& filename)', helper+'\tvoid FilePresenter::newThumbnailData(const std::string& filename)'),
    ('\t\t\tmodal.setImage(GetThumbnailPath(filename).c_str());', '\t\t\tmodal.setImage(GetThumbnailPath(filename).c_str());\n\t\t\tif (m_macroThumbnailPending)\n\t\t\t{\n\t\t\t\trequestSelectedMacroThumbnail(filename);\n\t\t\t}'),
    ('\t\tregisterEventListener<EventType::ThumbnailData>(this, &FilePresenter::newThumbnailData);', '\t\tregisterEventListener<EventType::ThumbnailData>(this, &FilePresenter::newThumbnailData);\n'+listener)])
edit('src/UI/Screens/File/FilePresenter.h', [
    ('\t\tvoid sortFiles();','\t\tvoid sortFiles();\n\t\tvoid requestSelectedMacroThumbnail(const std::string& filename);'),
    ('\t\tstd::string m_clickedItem;','\t\tstd::string m_clickedItem;\n\t\tbool m_macroThumbnailPending = false;')])
edit('src/UI/Screens/File/FileView.h', [
    ('void confirmRunMacro(std::string_view filename);','void confirmRunMacro(std::string_view filename, const std::filesystem::path& thumbnail);')])
edit('src/UI/Screens/File/FileView.cpp', [
    ('void FileView::confirmRunMacro(std::string_view filename)','void FileView::confirmRunMacro(std::string_view filename, const std::filesystem::path& thumbnail)'),
    ('m_startPrint.setOkCallback([this]() { m_presenter->runMacro(); });\n\t\tm_startPrint.setImage(nullptr);', 'm_startPrint.setOkCallback([this]() { m_presenter->runMacro(); });\n\t\tm_startPrint.setImage(IsThumbnailCached(thumbnail) ? thumbnail.c_str() : nullptr);')])

expected = {'src/Comm/FileInfo.cpp': 'f5afb915bee54c1b024619ac6c10522078f9d59c177581067851161fbacf7df9', 'src/Subscribers/FileSubscribers.cpp': '7bf4f299a19ea1b50f3040530d33549be7e5c90480e361c4b275a687c4aa2676', 'src/UI/Core/EventTypes.h': '304747410a242f5c7f48cf9ade1021aa8c0ef672aa644fd15ec19253a0709b7d', 'src/UI/Screens/File/FilePresenter.cpp': 'f53d02c4a0312b9d5f15e9fe4c6c0381904c8f1f78dd472866185bd3e48455ef', 'src/UI/Screens/File/FilePresenter.h': '22402ad125301d46a287bc6129bb1de44e003e443976f5e905722f8a52defa59', 'src/UI/Screens/File/FileView.cpp': '52a8dfd6b78ea75a9b8e7a33d2247c0ac683ac31968b6485dcd9507421b2d7cb', 'src/UI/Screens/File/FileView.h': '8283e5bc2b9dab051eb363183ffe91b399b941e76be1e6d4c7882b5f244c91b7'}
for name, digest in expected.items():
    actual = hashlib.sha256((root/name).read_bytes()).hexdigest()
    if actual != digest:
        raise RuntimeError(f'Modificación funcional alterada: {name}: {actual}')
print('Siete archivos de thumbnails idénticos al workflow funcional validado.')
