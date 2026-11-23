#include "json_loader.h"

#include <boost/json.hpp>
#include <boost/json/src.hpp>
#include <fstream>
#include <sstream>
#include <stdexcept>

namespace json = boost::json;
using namespace std::literals;

namespace json_loader {

namespace {

model::Road ParseRoad(const json::object& road_obj) {
    model::Coord x0 = static_cast<model::Coord>(road_obj.at("x0"sv).as_int64());
    model::Coord y0 = static_cast<model::Coord>(road_obj.at("y0"sv).as_int64());

    if (auto it = road_obj.find("x1"sv); it != road_obj.end()) {
        model::Coord x1 = static_cast<model::Coord>(it->value().as_int64());
        return model::Road(model::Road::HORIZONTAL, {x0, y0}, x1);
    }
    model::Coord y1 = static_cast<model::Coord>(road_obj.at("y1"sv).as_int64());
    return model::Road(model::Road::VERTICAL, {x0, y0}, y1);
}

model::Building ParseBuilding(const json::object& bld_obj) {
    model::Coord x = static_cast<model::Coord>(bld_obj.at("x"sv).as_int64());
    model::Coord y = static_cast<model::Coord>(bld_obj.at("y"sv).as_int64());
    model::Dimension w = static_cast<model::Dimension>(bld_obj.at("w"sv).as_int64());
    model::Dimension h = static_cast<model::Dimension>(bld_obj.at("h"sv).as_int64());
    return model::Building({{x, y}, {w, h}});
}

model::Office ParseOffice(const json::object& off_obj) {
    model::Office::Id id{std::string(off_obj.at("id"sv).as_string())};
    model::Coord x = static_cast<model::Coord>(off_obj.at("x"sv).as_int64());
    model::Coord y = static_cast<model::Coord>(off_obj.at("y"sv).as_int64());
    model::Dimension dx = static_cast<model::Dimension>(off_obj.at("offsetX"sv).as_int64());
    model::Dimension dy = static_cast<model::Dimension>(off_obj.at("offsetY"sv).as_int64());
    return model::Office(std::move(id), {x, y}, {dx, dy});
}

model::Map ParseMap(const json::object& map_obj) {
    model::Map::Id id{std::string(map_obj.at("id"sv).as_string())};
    std::string name(map_obj.at("name"sv).as_string());
    model::Map map(std::move(id), std::move(name));

    for (const auto& road_val : map_obj.at("roads"sv).as_array()) {
        map.AddRoad(ParseRoad(road_val.as_object()));
    }
    if (auto it = map_obj.find("buildings"sv); it != map_obj.end()) {
        for (const auto& bld_val : it->value().as_array()) {
            map.AddBuilding(ParseBuilding(bld_val.as_object()));
        }
    }
    if (auto it = map_obj.find("offices"sv); it != map_obj.end()) {
        for (const auto& off_val : it->value().as_array()) {
            map.AddOffice(ParseOffice(off_val.as_object()));
        }
    }
    return map;
}

}  // namespace

model::Game LoadGame(const std::filesystem::path& json_path) {
    std::ifstream file(json_path);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open config file: "s + json_path.string());
    }

    std::stringstream ss;
    ss << file.rdbuf();
    json::value doc = json::parse(ss.str());

    model::Game game;
    for (const auto& map_val : doc.as_object().at("maps"sv).as_array()) {
        game.AddMap(ParseMap(map_val.as_object()));
    }
    return game;
}

}  // namespace json_loader
