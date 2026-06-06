import extism

from pointiv_extension_sdk import bind


@extism.import_fn("extism:host", "pointiv_log")
def pointiv_log(msg: str):
    pass


@extism.import_fn("extism:host", "pointiv_storage_read")
def pointiv_storage_read(key: str) -> str:
    pass


@extism.import_fn("extism:host", "pointiv_storage_write")
def pointiv_storage_write(key: str, value: str):
    pass


@extism.import_fn("extism:host", "pointiv_storage_delete")
def pointiv_storage_delete(key: str):
    pass


@extism.import_fn("extism:host", "pointiv_http_request")
def pointiv_http_request(request_json: str) -> str:
    pass


@extism.import_fn("extism:host", "pointiv_google_calendar_create")
def pointiv_google_calendar_create(payload_json: str) -> str:
    pass


@extism.import_fn("extism:host", "pointiv_google_gmail_send")
def pointiv_google_gmail_send(payload_json: str) -> str:
    pass


bind.log_host(pointiv_log)
bind.storage_hosts(pointiv_storage_read, pointiv_storage_write, pointiv_storage_delete)
bind.http_host(pointiv_http_request)
bind.google_calendar_host(pointiv_google_calendar_create)
bind.google_gmail_host(pointiv_google_gmail_send)
