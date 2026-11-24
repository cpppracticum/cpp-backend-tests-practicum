#pragma once
#include "http_server.h"
#include "model.h"

namespace http_handler {

namespace beast = boost::beast;
namespace http = beast::http;

using StringRequest = http::request<http::string_body>;
using StringResponse = http::response<http::string_body>;

class RequestHandler {
public:
    explicit RequestHandler(model::Game& game)
        : game_{game} {
    }

    RequestHandler(const RequestHandler&) = delete;
    RequestHandler& operator=(const RequestHandler&) = delete;

    template <typename Body, typename Allocator, typename Send>
    void operator()(http::request<Body, http::basic_fields<Allocator>>&& req, Send&& send) {
        send(HandleRequest(std::move(req)));
    }

private:
    StringResponse HandleRequest(StringRequest&& req);
    model::Game& game_;
};

}  // namespace http_handler
