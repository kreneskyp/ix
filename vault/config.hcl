ui            = true
cluster_addr  = "https://0.0.0.0:8201"
api_addr      = "https://0.0.0.0:8200"
disable_mlock = true


storage "file" {
  path    = "/vault/file"
}


listener "tcp" {
  address     = "0.0.0.0:8200"

  tls_disable = false
  tls_cert_file = "/vault/certs/server.crt"
  tls_key_file  = "/vault/certs/server.key"
}

