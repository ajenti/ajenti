let socketIoConfig: any = {
  resource: `/socket.io`.substring(1),
  'reconnection limit': 1,
  'max reconnection attempts': 999999,
};

if (/Apple Computer/.test(navigator.vendor) && location.protocol === 'https:') {
  socketIoConfig.transports = [ 'jsonp-polling' ]; // Safari can go to hell
}

export { socketIoConfig }
