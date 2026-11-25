#include "request_handler.h"

#include <boost/json.hpp>

namespace json = boost::json;
using namespace std::literals;

namespace http_handler {

namespace {

StringResponse MakeJsonResponse(http::status status, std::string_view body, unsigned http_version,
                                bool keep_alive, bool is_head = false) {
    StringResponse response(status, http_version);
    response.set(http::field::content_type, "application/json"sv);
    response.set(http::field::cache_control, "no-cache"sv);
    response.content_length(body.size());
    if (!is_head) {
        response.body() = std::string(body);
    }
    response.keep_alive(keep_alive);
    return response;
}

StringResponse MakeErrorResponse(http::status status, std::string_view code, std::string_view message,
                                 unsigned http_version, bool keep_alive, bool is_head = false) {
    json::object err;
    err["code"sv] = code;
    err["message"sv] = message;
    return MakeJsonResponse(status, json::serialize(err), http_version, keep_alive, is_head);
}

json::object SerializeRoad(const model::Road& road) {
    json::object r;
    r["x0"sv] = road.GetStart().x;
    r["y0"sv] = road.GetStart().y;
    if (road.IsHorizontal()) {
        r["x1"sv] = road.GetEnd().x;
    } else {
        r["y1"sv] = road.GetEnd().y;
    }
    return r;
}

json::object SerializeBuilding(const model::Building& bld) {
    json::object b;
    b["x"sv] = bld.GetBounds().position.x;
    b["y"sv] = bld.GetBounds().position.y;
    b["w"sv] = bld.GetBounds().size.width;
    b["h"sv] = bld.GetBounds().size.height;
    return b;
}

json::object SerializeOffice(const model::Office& off) {
    json::object o;
    o["id"sv] = *off.GetId();
    o["x"sv] = off.GetPosition().x;
    o["y"sv] = off.GetPosition().y;
    o["offsetX"sv] = off.GetOffset().dx;
    o["offsetY"sv] = off.GetOffset().dy;
    return o;
}

json::array SerializeRoads(const model::Map::Roads& roads) {
    json::array arr;
    arr.reserve(roads.size());
    for (const auto& road : roads) {
        arr.push_back(SerializeRoad(road));
    }
    return arr;
}

json::array SerializeBuildings(const model::Map::Buildings& buildings) {
    json::array arr;
    arr.reserve(buildings.size());
    for (const auto& bld : buildings) {
        arr.push_back(SerializeBuilding(bld));
    }
    return arr;
}

json::array SerializeOffices(const model::Map::Offices& offices) {
    json::array arr;
    arr.reserve(offices.size());
    for (const auto& off : offices) {
        arr.push_back(SerializeOffice(off));
    }
    return arr;
}

json::value SerializeMapDetails(const model::Map& map) {
    json::object obj;
    obj["id"sv] = *map.GetId();
    obj["name"sv] = map.GetName();
    obj["roads"sv] = SerializeRoads(map.GetRoads());
    obj["buildings"sv] = SerializeBuildings(map.GetBuildings());
    obj["offices"sv] = SerializeOffices(map.GetOffices());
    return obj;
}

}  // namespace

StringResponse RequestHandler::HandleRequest(StringRequest&& req) {
    const auto version = req.version();
    const bool keep_alive = req.keep_alive();
    const bool is_head = (req.method() == http::verb::head);

    if (req.method() != http::verb::get && !is_head) {
        auto resp = MakeErrorResponse(http::status::method_not_allowed, "invalidMethod"sv,
                                      "Only GET and HEAD methods are expected"sv, version, keep_alive);
        resp.set(http::field::allow, "GET, HEAD"sv);
        return resp;
    }

    std::string_view target = req.target();
    constexpr std::string_view api_prefix = "/api/"sv;
    constexpr std::string_view maps_endpoint = "/api/v1/maps"sv;

    if (!target.starts_with(api_prefix)) {
        return MakeErrorResponse(http::status::bad_request, "badRequest"sv, "Bad request"sv, version,
                                 keep_alive, is_head);
    }

    if (target == maps_endpoint || target == "/api/v1/maps/"sv) {
        json::array maps_arr;
        for (const auto& map : game_.GetMaps()) {
            json::object m;
            m["id"sv] = *map.GetId();
            m["name"sv] = map.GetName();
            maps_arr.push_back(std::move(m));
        }
        return MakeJsonResponse(http::status::ok, json::serialize(maps_arr), version, keep_alive, is_head);
    }

    constexpr std::string_view map_prefix = "/api/v1/maps/"sv;
    if (target.starts_with(map_prefix)) {
        std::string_view map_id_str = target.substr(map_prefix.size());
        if (map_id_str.empty() || map_id_str.find('/') != std::string_view::npos) {
            return MakeErrorResponse(http::status::bad_request, "badRequest"sv, "Bad request"sv,
                                     version, keep_alive, is_head);
        }

        const auto* map = game_.FindMap(model::Map::Id{std::string(map_id_str)});
        if (!map) {
            return MakeErrorResponse(http::status::not_found, "mapNotFound"sv, "Map not found"sv,
                                     version, keep_alive, is_head);
        }
        return MakeJsonResponse(http::status::ok, json::serialize(SerializeMapDetails(*map)), version,
                                keep_alive, is_head);
    }

    return MakeErrorResponse(http::status::bad_request, "badRequest"sv, "Bad request"sv, version,
                             keep_alive, is_head);
}

}  // namespace http_handler
