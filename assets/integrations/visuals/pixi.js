import { Application, Graphics } from 'pixi.js';

export async function createScene(host, { width, height, seed = 1 }) {
  const app = new Application();
  await app.init({ width, height, background: 0x101629, antialias: true, autoStart: false, sharedTicker: false, preference: 'webgl' });
  app.stop();
  host.appendChild(app.canvas);
  const shape = new Graphics().circle(0, 0, Math.min(width, height) * .16).fill(0x67e8f9);
  app.stage.addChild(shape);
  const phase = Number(seed) * .01;
  return {
    drawAt(t) { shape.position.set(width * (.5 + .23 * Math.sin(t + phase)), height * .5); app.render(); },
    dispose() { app.destroy(true, { children: true }); }
  };
}
