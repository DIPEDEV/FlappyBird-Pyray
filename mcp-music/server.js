#!/usr/bin/env node
/**
 * MiniMax Music MCP Server
 * 
 * Setup:
 *   1. npm install
 *   2. node server.js
 * 
 * Your API key is already configured in openclaw.json
 * 
 * MiniMax API docs: https://platform.minimax.io/docs/api-reference/music-generation
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// MiniMax API key (from your openclaw config)
const API_KEY = 'sk-cp-RnLIfKD4VKg33SzCKRhR3pGBykLu1lLLSy0D8hipK3suMJNQI8Q4wDYFmNRPeJpY4JmOAjkA1cFNyJ30ZjTZ9HTESLtHn0zB0_JESInzbrSz59iv4eEAF-g';
const BASE_HOST = 'api.minimax.io';

// MCP Protocol - read JSON-RPC from stdin, write to stdout
let buffer = '';

process.stdin.on('data', (chunk) => {
  buffer += chunk;
  const lines = buffer.split('\n');
  buffer = lines.pop();
  
  for (const line of lines) {
    if (line.trim()) {
      try {
        const request = JSON.parse(line);
        handleRequest(request);
      } catch (e) {
        // Ignore incomplete JSON
      }
    }
  }
});

process.stdin.on('end', () => {
  if (buffer.trim()) {
    try {
      const request = JSON.parse(buffer);
      handleRequest(request);
    } catch (e) {}
  }
});

function sendResponse(id, result) {
  const response = { jsonrpc: '2.0', id, result };
  console.log(JSON.stringify(response));
}

function sendError(id, code, message) {
  const response = { jsonrpc: '2.0', id, error: { code, message } };
  console.log(JSON.stringify(response));
}

async function handleRequest(request) {
  const { id, method, params } = request;
  
  try {
    if (method === 'initialize') {
      sendResponse(id, {
        protocolVersion: '2024-11-05',
        capabilities: { tools: {} },
        serverInfo: { name: 'minimax-music', version: '1.0.0' }
      });
    }
    else if (method === 'tools/list') {
      sendResponse(id, {
        tools: [
          {
            name: 'generate_music',
            description: 'Generate music using MiniMax API. Creates a song from a text prompt (style/mood/genre). Returns a URL or saves to file.',
            inputSchema: {
              type: 'object',
              properties: {
                prompt: { type: 'string', description: 'Music description: genre, mood, instruments, tempo (e.g. "Chill lo-fi, upbeat, 8-bit retro game music")' },
                duration: { type: 'number', description: 'Duration in seconds (default: 15, max: 120)', default: 15 },
                outputPath: { type: 'string', description: 'Local path to save the audio file (optional)' }
              },
              required: ['prompt']
            }
          },
          {
            name: 'generate_music_with_lyrics',
            description: 'Generate music with custom lyrics. Creates a full song with vocals from your lyrics.',
            inputSchema: {
              type: 'object',
              properties: {
                prompt: { type: 'string', description: 'Music style description (e.g. "Soulful Blues, Rainy Night, Slow Tempo")' },
                lyrics: { type: 'string', description: 'Song lyrics with section markers like [Verse], [Chorus]' },
                duration: { type: 'number', description: 'Duration in seconds (default: 60)' },
                outputPath: { type: 'string', description: 'Local path to save the audio file (optional)' }
              },
              required: ['prompt', 'lyrics']
            }
          },
          {
            name: 'generate_sound_effect',
            description: 'Generate sound effects using MiniMax API.',
            inputSchema: {
              type: 'object',
              properties: {
                prompt: { type: 'string', description: 'Sound effect description (e.g. "flappy bird wing sound, cheerful")' },
                duration: { type: 'number', description: 'Duration in seconds (default: 5)' },
                outputPath: { type: 'string', description: 'Local path to save the audio file (optional)' }
              },
              required: ['prompt']
            }
          }
        ]
      });
    }
    else if (method === 'tools/call') {
      const { name, arguments: args } = params;
      
      if (name === 'generate_music') {
        const result = await generateMusic(args.prompt, args.duration || 15, args.outputPath);
        sendResponse(id, { content: [{ type: 'text', text: result }] });
      }
      else if (name === 'generate_music_with_lyrics') {
        const result = await generateMusicWithLyrics(args.prompt, args.lyrics, args.duration || 60, args.outputPath);
        sendResponse(id, { content: [{ type: 'text', text: result }] });
      }
      else if (name === 'generate_sound_effect') {
        const result = await generateSoundEffect(args.prompt, args.duration || 5, args.outputPath);
        sendResponse(id, { content: [{ type: 'text', text: result }] });
      }
      else {
        sendError(id, -32601, `Unknown tool: ${name}`);
      }
    }
    else if (method === 'notifications/initialized') {
      // Ignore
    }
    else {
      sendError(id, -32601, `Unknown method: ${method}`);
    }
  } catch (error) {
    console.error('Error:', error.message);
    sendError(id, -32603, error.message);
  }
}

function makeApiRequest(path, body) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: BASE_HOST,
      port: 443,
      path: path,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch {
          resolve({ raw: data });
        }
      });
    });

    req.on('error', reject);
    req.write(JSON.stringify(body));
    req.end();
  });
}

async function pollForResult(groupId, timeout = 60000) {
  const startTime = Date.now();
  const pollInterval = 2000;
  
  while (Date.now() - startTime < timeout) {
    const response = await makeApiRequest('/v1/music_generation', {
      model: 'music-2.6',
      action: 'query',
      group_id: groupId
    });
    
    if (response.status === 1 && response.data && response.data.audio_url) {
      return response.data.audio_url;
    }
    
    if (response.status === 2) {
      throw new Error('Music generation failed');
    }
    
    await new Promise(resolve => setTimeout(resolve, pollInterval));
  }
  
  throw new Error('Timeout waiting for music generation');
}

async function generateMusic(prompt, duration = 15, outputPath) {
  try {
    console.error(`Generating music: ${prompt} (${duration}s)`);
    
    const response = await makeApiRequest('/v1/music_generation', {
      model: 'music-2.6',
      prompt: prompt,
      duration: duration,
      audio_setting: {
        sample_rate: 44100,
        bitrate: 256000,
        format: 'mp3'
      },
      output_format: 'url'
    });
    
    let audioUrl;
    
    if (response.status === 1 && response.data && response.data.audio_url) {
      audioUrl = response.data.audio_url;
    }
    else if (response.status === 0 && response.data && response.data.group_id) {
      // Poll for completion
      audioUrl = await pollForResult(response.data.group_id);
    }
    else {
      return `Music generation response: ${JSON.stringify(response)}`;
    }
    
    if (outputPath) {
      await downloadFile(audioUrl, outputPath);
      return `Music generated and saved to: ${outputPath}`;
    }
    
    return `Music generated successfully! Audio URL: ${audioUrl}`;
  } catch (error) {
    return `Error generating music: ${error.message}`;
  }
}

async function generateMusicWithLyrics(prompt, lyrics, duration = 60, outputPath) {
  try {
    console.error(`Generating music with lyrics: ${prompt}`);
    
    const response = await makeApiRequest('/v1/music_generation', {
      model: 'music-2.6',
      prompt: prompt,
      lyrics: lyrics,
      duration: duration,
      audio_setting: {
        sample_rate: 44100,
        bitrate: 256000,
        format: 'mp3'
      },
      output_format: 'url'
    });
    
    let audioUrl;
    
    if (response.status === 1 && response.data && response.data.audio_url) {
      audioUrl = response.data.audio_url;
    }
    else if (response.status === 0 && response.data && response.data.group_id) {
      audioUrl = await pollForResult(response.data.group_id);
    }
    else {
      return `Music generation response: ${JSON.stringify(response)}`;
    }
    
    if (outputPath) {
      await downloadFile(audioUrl, outputPath);
      return `Song generated and saved to: ${outputPath}`;
    }
    
    return `Song generated successfully! Audio URL: ${audioUrl}`;
  } catch (error) {
    return `Error generating song: ${error.message}`;
  }
}

async function generateSoundEffect(prompt, duration = 5, outputPath) {
  // MiniMax doesn't have a separate SFX API in this version
  // Try using music generation with very short duration
  return generateMusic(prompt, duration, outputPath);
}

async function downloadFile(url, filePath) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(filePath);
    const request = https.get(url, (res) => {
      res.pipe(file);
      file.on('finish', () => {
        file.close();
        console.error(`Downloaded: ${filePath}`);
        resolve();
      });
    });
    request.on('error', (err) => {
      fs.unlink(filePath, () => {});
      reject(err);
    });
  });
}

console.error('MiniMax Music MCP Server started');