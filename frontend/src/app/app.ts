import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { API_CONFIG } from '../config/api.config';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class AppComponent {
  question = '';
  isLoading = false;
  status = '';
  private websocket?: WebSocket;
  private audioContext?: AudioContext;
  private audioQueue: AudioBuffer[] = [];
  private isPlaying = false;

  constructor(private http: HttpClient) {}

  async askQuestion() {
    if (!this.question.trim()) return;

    this.isLoading = true;
    this.status = 'Sending question...';
    this.audioQueue = [];

    try {
      // Initialize audio context
      this.audioContext = new AudioContext();
      
      const response = await this.http.post<{session_id: string}>(
        `${API_CONFIG.BASE_URL}/ask`,
        { question: this.question }
      ).toPromise();

      if (response?.session_id) {
        this.status = 'Connecting to audio stream...';
        this.connectWebSocket(response.session_id);
      }
    } catch (error) {
      this.status = 'Error sending question';
      this.isLoading = false;
    }
  }

  private connectWebSocket(sessionId: string) {
    this.websocket = new WebSocket(`${API_CONFIG.WEBSOCKET_URL}/${sessionId}`);

    this.websocket.onopen = () => {
      this.status = 'Connected. Receiving audio...';
    };

    this.websocket.onmessage = async (event) => {
      if (event.data === "END") {
        this.status = 'Audio stream complete';
        this.isLoading = false;
        return;
      }

      if (event.data instanceof Blob) {
        try {
          const arrayBuffer = await event.data.arrayBuffer();
          const audioBuffer = await this.audioContext!.decodeAudioData(arrayBuffer);
          this.audioQueue.push(audioBuffer);
          
          if (!this.isPlaying) {
            this.playNextChunk();
          }
        } catch (error) {
          console.error('Error processing audio chunk:', error);
        }
      }
    };

    this.websocket.onclose = () => {
      this.isLoading = false;
    };

    this.websocket.onerror = () => {
      this.status = 'WebSocket connection error';
      this.isLoading = false;
    };
  }

  private async playNextChunk() {
    if (this.audioQueue.length === 0) {
      this.isPlaying = false;
      return;
    }

    this.isPlaying = true;
    const audioBuffer = this.audioQueue.shift()!;
    const source = this.audioContext!.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(this.audioContext!.destination);
    
    source.onended = () => {
      this.playNextChunk();
    };
    
    source.start();
  }

  ngOnDestroy() {
    this.websocket?.close();
    this.audioContext?.close();
  }
}
