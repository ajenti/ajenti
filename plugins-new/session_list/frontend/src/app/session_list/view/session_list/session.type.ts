export interface ClientInfo {
  ipv4_address: string,
}

export interface Session {
  identity: string;
  timestamp: number;
  client_info: ClientInfo;
}
