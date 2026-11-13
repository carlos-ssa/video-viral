import transitions from 'gl-transitions';

export async function createScene(host, { width, height, seed = 1, duration = 4, imageA, imageB }) {
  const canvas = document.createElement('canvas'); canvas.width = width; canvas.height = height; host.appendChild(canvas);
  const gl = canvas.getContext('webgl', { preserveDrawingBuffer: true, antialias: false });
  if (!gl) { canvas.remove(); throw new Error('WebGL is required for gl-transitions'); }
  const transition = transitions.find(item => item.name.toLowerCase() === 'crosswarp');
  if (!transition) throw new Error('gl-transitions CrossWarp shader is unavailable');
  function compile(type, source) {
    const shader = gl.createShader(type); gl.shaderSource(shader, source); gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(shader));
    return shader;
  }
  const vs = compile(gl.VERTEX_SHADER, 'attribute vec2 position; varying vec2 uv; void main(){uv=(position+1.0)*0.5;gl_Position=vec4(position,0.0,1.0);}');
  const fs = compile(gl.FRAGMENT_SHADER, `precision mediump float; varying vec2 uv; uniform float progress; uniform sampler2D fromTex; uniform sampler2D toTex; vec4 getFromColor(vec2 p){return texture2D(fromTex,p);} vec4 getToColor(vec2 p){return texture2D(toTex,p);} ${transition.glsl}\nvoid main(){gl_FragColor=transition(uv);}`);
  const program = gl.createProgram(); gl.attachShader(program, vs); gl.attachShader(program, fs); gl.linkProgram(program);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(program));
  gl.useProgram(program);
  const buffer = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buffer); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
  const position = gl.getAttribLocation(program, 'position'); gl.enableVertexAttribArray(position); gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);
  const textures = [[16,22,41,255], [50 + (Math.abs(Number(seed)) % 150),180,220,255]].map((color, i) => {
    const texture = gl.createTexture(); gl.activeTexture(gl.TEXTURE0 + i); gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array(color));
    gl.uniform1i(gl.getUniformLocation(program, i ? 'toTex' : 'fromTex'), i); return texture;
  });
  if (imageA && imageB) {
    const images = await Promise.all([imageA, imageB].map(async src => {
      const image = new Image(); image.src = src; await image.decode(); return image;
    }));
    images.forEach((image, index) => {
      const fitted = document.createElement('canvas'); fitted.width = width; fitted.height = height;
      const ctx = fitted.getContext('2d'); ctx.fillStyle = '#101629'; ctx.fillRect(0, 0, width, height);
      const scale = Math.min(width / image.width, height / image.height);
      ctx.drawImage(image, (width - image.width * scale) / 2, (height - image.height * scale) / 2,
        image.width * scale, image.height * scale);
      gl.activeTexture(gl.TEXTURE0 + index); gl.bindTexture(gl.TEXTURE_2D, textures[index]);
      gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, fitted);
    });
  }
  return {
    drawAt(t) { gl.viewport(0, 0, width, height); gl.uniform1f(gl.getUniformLocation(program, 'progress'), Math.max(0, Math.min(1, t / duration))); gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4); },
    dispose() { textures.forEach(texture => gl.deleteTexture(texture)); gl.deleteBuffer(buffer); gl.deleteProgram(program); gl.deleteShader(vs); gl.deleteShader(fs); canvas.remove(); }
  };
}
