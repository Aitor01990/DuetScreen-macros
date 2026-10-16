// Ejecuta el selector C++ utilizado realmente por UpgradeHelper, con HTTP simulado.
#include "IndartVersionPolicy.h"
#include <nlohmann/json.hpp>
#include <cassert>
#include <iostream>
#include <map>
#include <string>
#include <vector>
#define FIRMWARE_VERSION "v1.0.0.1"
#define INDART_UPDATE_REPOSITORY "Aitor01990/DuetScreen-macros"
#define INDART_RELEASES_PATH "/repos/" INDART_UPDATE_REPOSITORY "/releases"
#define UPGRADE_FILE "DuetScreen.tar.gz"
#define HTTP_GET 1
#define HTTP_TIMEOUT 10
#define HTTP_STATUS_OK 200
#define LOG_WARN(...) ((void)0)
struct HttpRequest {
    int method{}, timeout{};
    std::string scheme, host, path;
    std::map<std::string, std::string> headers;
    void DumpUrl() {}
};
struct HttpResponse { int status_code = 200; std::string body; };
static std::vector<HttpResponse> responses;
static size_t requestIndex;
namespace hv {
struct HttpClient {
    void send(HttpRequest* req, HttpResponse* response) {
        assert(req->host == "api.github.com");
        assert(req->scheme == "https");
        assert(req->path == std::string(INDART_RELEASES_PATH)+"?per_page=100&page="+std::to_string(requestIndex+1));
        assert(requestIndex < responses.size());
        *response = responses[requestIndex++];
    }
};
}
struct GithubReleaseInfo { std::string tag, downloadUrl; };
#include "../patches/github_release_selection.cpp.txt"

static nlohmann::json release(std::string tag) {
    return {{"tag_name", tag}, {"draft", false}, {"prerelease", false},
        {"assets", {{{"name", UPGRADE_FILE}, {"browser_download_url", std::string("https://github.com/")+INDART_UPDATE_REPOSITORY+"/releases/download/"+tag+"/"+UPGRADE_FILE}}}}};
}
static std::optional<GithubReleaseInfo> run(nlohmann::json payload) {
    responses = {{200, payload.dump()}}; requestIndex = 0;
    return getNewestGithubReleaseWithUpgradeAsset();
}
int main() {
    for (const auto* bad : {"", "v1.0.0", "1.0.0.1", "v1.0.0.2-rc1", "v1.0.0.2x", "v1..0.1", "v1.0.0.65536", "v1.0.0.12345678912345", "v1.0.0.2.1"})
        assert(!Indart::parseStableVersion(bad));
    assert(Indart::parseStableVersion("v1.0.0.10") > Indart::parseStableVersion("v1.0.0.2"));
    auto stable = release("v1.0.0.2");
    auto draft = release("v1.0.0.30"); draft["draft"] = true;
    auto pre = release("v1.0.0.40"); pre["prerelease"] = true;
    auto missing = release("v1.0.0.50"); missing["assets"] = nlohmann::json::array();
    auto wrong = release("v1.0.0.60"); wrong["assets"][0]["browser_download_url"] = "https://example.com/DuetScreen.tar.gz";
    auto malformed = release("v1.0.0.70"); malformed["draft"] = "false";
    auto selected = run(nlohmann::json::array({stable, draft, pre, missing, wrong, malformed, release("v1.0.0.10"), release("v1.0.0.3")}));
    assert(selected && selected->tag == "v1.0.0.10");
    assert(!run(nlohmann::json::array({release("v1.0.0.1"), release("v1.0.0.0"), release("v1.0.0"), release("v1.0.0.2-beta")})));
    assert(!run(nlohmann::json::object()));
    assert(!run(nlohmann::json::array({nullptr, 1, "bad"})));
    nlohmann::json full = nlohmann::json::array();
    for (int i=0; i<100; ++i) full.push_back(draft);
    responses = {{200, full.dump()}, {200, nlohmann::json::array({stable}).dump()}}; requestIndex=0;
    assert(getNewestGithubReleaseWithUpgradeAsset()->tag == "v1.0.0.2");
    responses = {{200, full.dump()}, {403, "{}"}}; requestIndex=0;
    assert(!getNewestGithubReleaseWithUpgradeAsset());
    responses = {{200, "not json"}}; requestIndex=0;
    assert(!getNewestGithubReleaseWithUpgradeAsset());
    responses.assign(10, {200, full.dump()}); requestIndex=0;
    assert(!getNewestGithubReleaseWithUpgradeAsset());
    std::cout << "C++ OK: four components, overflow, stable filtering, highest version, assets, origin, pagination, HTTP/JSON errors.\n";
}
