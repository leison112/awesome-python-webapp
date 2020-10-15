# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import asyncio
import json
import logging

from aiohttp import web, web_request

import config
import coroweb
import orm

logging.basicConfig(level='DEBUG',
                    format='[%(asctime)s.%(msecs)-3d] [%(levelname)-6s] [%(module)s.%(funcName)s:%(lineno)d] [%(threadName)s] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


async def index(request):
    # await asyncio.sleep(10)
    return '<h1>Awesome</h1>'


@asyncio.coroutine
def init_2(loop):
    app = web.Application(loop=loop)
    app.router.add_route(method='GET', path='/', handler=index)
    srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000')
    return srv


async def log_middleware(app, handler):
    async def logger(request: web_request.Request):
        logging.info('Request: %s %s' % (request.method, request.path))
        ct = request.content_type.lower()
        if ct.startswith('application/json'):
            logging.info('Request json: %s' % str(await request.json()))
        elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
            logging.info('Request form: %s' % str(await request.post()))
        else:
            logging.info('Request query_string: %s' % request.query_string)
        return await handler(request)

    return logger


async def response_middleware(app, handler):
    async def response(request: web_request.Request):
        r = await handler(request)
        if isinstance(r, web.StreamResponse):
            return r
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(r, str):
            if r.startswith('redirect:'):
                return web.HTTPFound(r[9:])
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(r, dict):
            template = r.get('__template__')
            if template is None:
                resp = web.Response(
                    body=json.dumps(r, ensure_ascii=False).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                return resp
        resp = web.Response(body=str(r).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
        return resp

    return response


async def init():
    await orm.create_pool(host=config.configs['db']['host'])
    app = web.Application(middlewares=[log_middleware, response_middleware])
    app.router.add_route(method='GET', path='/', handler=index)
    coroweb.add_routes(app, 'handlers')
    coroweb.add_static(app)
    app_runner = web.AppRunner(app)
    await app_runner.setup()
    site = web.TCPSite(app_runner, '127.0.0.1', 9000)
    await site.start()
    logging.info('server started at http://127.0.0.1:9000')


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    logging.info(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())
    loop.run_forever()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
