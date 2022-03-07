import ssl

def get_context_tls():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(
        "/path_certificate/eventview/config/cert/cert.crt",
        "/path_key/eventview/config/key/key.key"
        )
    context.set_ciphers("ECDHE-RSA-AES256-GCM-SHA384")

    return context
