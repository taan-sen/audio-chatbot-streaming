export const API_CONFIG = {
  BASE_URL: '/api',
  WEBSOCKET_URL: `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/ws/voice`
};
