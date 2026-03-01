/**
 * WebSocket Service for Vue 3
 * Real-time communication with WebSocket server
 */

import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

// Message types
export const MessageType = {
  CONNECTION_INIT: 'CONNECTION_INIT',
  CONNECTION_ACK: 'CONNECTION_ACK',
  CONNECTION_ERROR: 'CONNECTION_ERROR',
  PROGRESS_UPDATE: 'PROGRESS_UPDATE',
  TASK_COMPLETE: 'TASK_COMPLETE',
  TASK_ERROR: 'TASK_ERROR',
  NOTIFICATION: 'NOTIFICATION',
  PING: 'PING',
  PONG: 'PONG',
}

// Connection state
export const ConnectionState = {
  DISCONNECTED: 'disconnected',
  CONNECTING: 'connecting',
  CONNECTED: 'connected',
  RECONNECTING: 'reconnecting',
}

class WebSocketService {
  private ws: WebSocket | null = null
  private connectionId: string | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 10
  private reconnectDelay = 1000
  private maxReconnectDelay = 30000
  private heartbeatInterval: number | null = null
  private state = ref(ConnectionState.DISCONNECTED)
  private lastMessage = ref<any>(null)
  private listeners: Map<string, Set<(data: any) => void>> = new Map()

  /**
   * Connect to WebSocket server
   */
  connect(token: string) {
    if (this.ws) {
      return
    }

    this.state.value = ConnectionState.CONNECTING

    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/notifications?token=${token}`

    this.ws = new WebSocket(wsUrl)

    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.state.value = ConnectionState.CONNECTED
      this.reconnectAttempts = 0
      this.startHeartbeat()
    }

    this.ws.onclose = (event) => {
      console.log('WebSocket closed', event.code, event.reason)
      this.state.value = ConnectionState.DISCONNECTED
      this.stopHeartbeat()
      this.ws = null

      // Attempt reconnection
      if (event.code !== 4001 && event.code !== 4002 && event.code !== 4003 && event.code !== 4004) {
        this.scheduleReconnect(token)
      }
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        this.lastMessage.value = message
        this.handleMessage(message)
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }
  }

  /**
   * Handle incoming messages
   */
  private handleMessage(message: any) {
    const { type, data } = message

    switch (type) {
      case MessageType.CONNECTION_ACK:
        this.connectionId = data.connection_id
        console.log('WebSocket connection acknowledged, ID:', this.connectionId)
        break

      case MessageType.PROGRESS_UPDATE:
        this.emit('progress', data)
        break

      case MessageType.TASK_COMPLETE:
        this.emit('complete', data)
        break

      case MessageType.TASK_ERROR:
        this.emit('error', data)
        break

      case MessageType.NOTIFICATION:
        this.emit('notification', data)
        break

      case MessageType.PONG:
        // Heartbeat response - connection is alive
        break
    }
  }

  /**
   * Schedule reconnection with exponential backoff
   */
  private scheduleReconnect(token: string) {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      return
    }

    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts),
      this.maxReconnectDelay
    )

    console.log(`Reconnecting in ${delay}ms... (attempt ${this.reconnectAttempts + 1})`)

    this.state.value = ConnectionState.RECONNECTING
    this.reconnectAttempts++

    setTimeout(() => {
      this.connect(token)
    }, delay)
  }

  /**
   * Start heartbeat
   */
  private startHeartbeat() {
    this.heartbeatInterval = window.setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send({ type: MessageType.PING })
      }
    }, 30000) // 30 seconds
  }

  /**
   * Stop heartbeat
   */
  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  /**
   * Send message to server
   */
  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket is not connected')
    }
  }

  /**
   * Join a room
   */
  joinRoom(room: string) {
    this.send({ type: 'JOIN_ROOM', room })
  }

  /**
   * Leave a room
   */
  leaveRoom(room: string) {
    this.send({ type: 'LEAVE_ROOM', room })
  }

  /**
   * Subscribe to event
   */
  on(event: string, callback: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)!.add(callback)
  }

  /**
   * Unsubscribe from event
   */
  off(event: string, callback: (data: any) => void) {
    const eventListeners = this.listeners.get(event)
    if (eventListeners) {
      eventListeners.delete(callback)
    }
  }

  /**
   * Emit event to listeners
   */
  private emit(event: string, data: any) {
    const eventListeners = this.listeners.get(event)
    if (eventListeners) {
      eventListeners.forEach(callback => callback(data))
    }
  }

  /**
   * Disconnect from server
   */
  disconnect() {
    this.stopHeartbeat()
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.state.value = ConnectionState.DISCONNECTED
    this.connectionId = null
  }

  /**
   * Get connection state
   */
  getState() {
    return this.state.value
  }

  /**
   * Check if connected
   */
  isConnected() {
    return this.state.value === ConnectionState.CONNECTED
  }
}

// Global instance
export const wsService = new WebSocketService()

/**
 * Vue composable for WebSocket
 */
export function useWebSocket() {
  const authStore = useAuthStore()

  const connect = () => {
    if (authStore.accessToken) {
      wsService.connect(authStore.accessToken)
    }
  }

  const disconnect = () => {
    wsService.disconnect()
  }

  const onProgress = (callback: (data: any) => void) => {
    wsService.on('progress', callback)
  }

  const onComplete = (callback: (data: any) => void) => {
    wsService.on('complete', callback)
  }

  const onError = (callback: (data: any) => void) => {
    wsService.on('error', callback)
  }

  const onNotification = (callback: (data: any) => void) => {
    wsService.on('notification', callback)
  }

  const joinRoom = (room: string) => {
    wsService.joinRoom(room)
  }

  const leaveRoom = (room: string) => {
    wsService.leaveRoom(room)
  }

  return {
    connect,
    disconnect,
    onProgress,
    onComplete,
    onError,
    onNotification,
    joinRoom,
    leaveRoom,
    state: wsService.state,
    isConnected: wsService.isConnected,
  }
}
