#pragma once
#include <array>
#include <cstdint>
#include <optional>
#include <string_view>

namespace Indart
{
using Version = std::array<uint32_t, 4>;

// Canal estable INDART3D: exactamente vA.B.C.D, sin sufijos ni desbordamientos.
inline std::optional<Version> parseStableVersion(std::string_view text)
{
    if (text.empty() || text.front() != 'v') return std::nullopt;
    text.remove_prefix(1);
    Version result{};
    for (size_t i = 0; i < result.size(); ++i)
    {
        size_t digits = 0;
        while (!text.empty() && text.front() >= '0' && text.front() <= '9')
        {
            if (++digits > 5) return std::nullopt;
            result[i] = result[i] * 10 + static_cast<uint32_t>(text.front() - '0');
            if (result[i] > 65535) return std::nullopt;
            text.remove_prefix(1);
        }
        if (!digits) return std::nullopt;
        if (i < result.size() - 1)
        {
            if (text.empty() || text.front() != '.') return std::nullopt;
            text.remove_prefix(1);
        }
    }
    if (!text.empty()) return std::nullopt;
    return result;
}
} // namespace Indart
