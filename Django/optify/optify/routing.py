
from channels.routing import ProtocolTypeRouter, URLRouter
import chat.routing
from chat.middlewares import TokenAuthMiddleware

application = ProtocolTypeRouter({
  'websocket': TokenAuthMiddleware(
    URLRouter(
    chat.routing.websocket_urlpatterns # send request to chatter's urls
    )
  )
})