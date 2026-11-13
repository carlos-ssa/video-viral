import paper from 'paper';

export async function createScene(host, { width, height, seed = 1 }) {
  const canvas = document.createElement('canvas');
  canvas.width = width; canvas.height = height; host.appendChild(canvas);
  const scope = new paper.PaperScope(); scope.setup(canvas);
  const background = new scope.Path.Rectangle(new scope.Point(0, 0), new scope.Size(width, height));
  background.fillColor = '#101629';
  const shape = new scope.Path.Circle(new scope.Point(width / 2, height / 2), Math.min(width, height) * .16);
  shape.fillColor = '#67e8f9';
  return {
    drawAt(t) { shape.position = new scope.Point(width * (.5 + .23 * Math.sin(t + Number(seed) * .01)), height * .5); scope.view.update(); },
    dispose() { scope.project.remove(); canvas.remove(); }
  };
}
