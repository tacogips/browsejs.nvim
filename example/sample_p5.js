//
// {% start header_tag %}
// <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.1.9/p5.min.js"></script>
// {% end %}
//
// {% start custom_tag %}
// <main></main>
// {% end %}
//
// {% start style  %}
// body {padding: 0; margin: 0;} canvas {vertical-align: top;}
// {% end %}

let stars = []; //star array

function setup() {
  createCanvas(800, 600);

  for (let i = 0; i < 800; i++) {
    //make a star array, and the array is a star function.
    stars[i] = new Star();
  }
}

function draw() {
  //background change
  background(26, 28, 54);

  //call the star show function
  push();
  translate(width / 2, height / 2);
  for (let i = 0; i < stars.length; i++) {
    stars[i].show();
  }
  pop();
}

class Star {
  x = random(-width, width);
  y = random(-height, height);
  z = random(width);

  show() {
    this.speed = map(mouseY, 0, height, 10, 5);
    this.z = this.z - this.speed;

    if (this.z < 1) {
      this.z = width;
      this.x = random(-width, width);
      this.y = random(-height, height);
    }

    fill(255);
    noStroke();
    this.sx = map(this.x / this.z, 0, 1, 0, width);
    this.sy = map(this.y / this.z, 0, 1, 0, height);
    this.r = map(this.z, 0, width, 8, 0);
    ellipse(this.sx, this.sy, this.r, this.r);
  }
}
