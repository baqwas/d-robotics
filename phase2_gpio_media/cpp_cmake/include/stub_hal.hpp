// ============================================================================
// File:        stub_hal.hpp
// Project:     d-robotics (ParkCircus Productions)
// License:     MIT
// Description: Hardware abstraction stub declarations for Phase 2 C++ media
//              and GPIO pipelines when building with RDKX3_STUB_HARDWARE=1.
// ============================================================================

#ifndef RDK_X3_PHASE2_STUB_HAL_HPP
#define RDK_X3_PHASE2_STUB_HAL_HPP

#include <cstdint>
#include <string>

namespace rdkx3::phase2 {

struct MediaFrameInfo {
    std::string input_path;
    std::string output_path;
    int width{0};
    int height{0};
    std::uint64_t frame_index{0};
    bool stub_mode{false};
};

std::string current_utc_waqt();
std::string default_device_id();
bool process_media_file(const std::string& input_path,
                        const std::string& output_path,
                        MediaFrameInfo& out_info);

}  // namespace rdkx3::phase2

#endif  // RDK_X3_PHASE2_STUB_HAL_HPP
