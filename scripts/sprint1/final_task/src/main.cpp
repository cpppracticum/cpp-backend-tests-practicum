#ifdef WIN32
#include <sdkddkver.h>
#endif

#include "http_server.h"

#include <boost/asio/signal_set.hpp>
#include <iostream>
#include <thread>
#include <vector>

namespace net = boost::asio;
using tcp = net::ip::tcp;
namespace beast = boost::beast;
namespace http = beast::http;
using namespace std::literals;

using StringRequest = http::request<http::string_body>;
using StringResponse = http::response<http::string_body>;

template <typename Fn>
void RunWorkers(unsigned num_threads, const Fn& fn) {
    num_threads = std::max(1u, num_threads);
    std::vector<std::jthread> workers;
    workers.reserve(num_threads - 1);
    while (--num_threads) {
        workers.emplace_back(fn);
    }
    fn();
}

StringResponse HandleRequest(StringRequest&& req) {
    if (req.method() != http::verb::get && req.method() != http::verb::head) {
        StringResponse response(http::status::method_not_allowed, req.version());
        response.set(http::field::content_type, "text/html"sv);
        response.set(http::field::allow, "GET, HEAD"sv);
        response.body() = "Invalid method."s;
        response.content_length(response.body().size());
        response.keep_alive(req.keep_alive());
        return response;
    }

    StringResponse response(http::status::ok, req.version());
    response.set(http::field::content_type, "text/html"sv);

    std::string_view target = req.target();
    if (!target.empty() && target.front() == '/') {
        target.remove_prefix(1);
    }

    std::string body = "Hello, "s + std::string(target);
    response.content_length(body.size());

    if (req.method() == http::verb::get) {
        response.body() = std::move(body);
    }

    response.keep_alive(req.keep_alive());
    return response;
}

int main() {
    const unsigned num_threads = std::thread::hardware_concurrency();
    net::io_context ioc(num_threads);

    net::signal_set signals(ioc, SIGINT, SIGTERM);
    signals.async_wait([&ioc](const boost::system::error_code& ec, [[maybe_unused]] int signal_number) {
        if (!ec) {
            ioc.stop();
        }
    });

    const auto address = net::ip::make_address("0.0.0.0");
    constexpr net::ip::port_type port = 8080;

    http_server::ServeHttp(ioc, {address, port}, [](auto&& req, auto&& sender) {
        sender(HandleRequest(std::forward<decltype(req)>(req)));
    });

    std::cout << "Server has started..."sv << std::endl;

    RunWorkers(num_threads, [&ioc] {
        ioc.run();
    });

    return 0;
}
