import p5 from 'p5';

export async function createScene(host, { width, height, seed = 1 }) {
  let instance;
  await new Promise((resolve, reject) => {
    try {
      instance = new p5(p => {
        p.setup = () => { p.pixelDensity(1); p.createCanvas(width, height); p.noLoop(); resolve(); };
      }, host);
    } catch (error) { reject(error); }
  });
  return {
    drawAt(t) {
      instance.background('#101629'); instance.noStroke(); instance.fill('#67e8f9');
      instance.circle(width * (.5 + .23 * Math.sin(t + Number(seed) * .01)), height * .5, Math.min(width, height) * .32);
    },
    dispose() { instance.remove(); }
  };
}
