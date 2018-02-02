/* ARTFACEAPP: render_colors.js - script for rendering photo filters for 1910, 1920, 1930, 1950 and 1970 
 * script runs with Node.js and uses caman.js and node-easel 
*/
'use strict'

var Canvas = require('/opt/caffe/node_modules/canvas'), Image = Canvas.Image
var Caman = require('/opt/caffe/node_modules/caman').Caman;

/* Color Matrices for specific photo filters */
var desaturateLuminance = [0.2764723, 0.9297080, 0.0938197, 0, -37.1,
			0.2764723, 0.9297080, 0.0938197, 0, -37.1,
			0.2764723, 0.9297080, 0.0938197, 0, -37.1,
			0, 0, 0, 1, 0];

var sepia = [0.393, 0.7689999, 0.18899999, 0, 0,
			0.349, 0.6859999, 0.16799999, 0, 0,
			0.272, 0.5339999, 0.13099999, 0, 0,
			0,0,0,1,0];

var brownie = [ 0.5997023498159715,0.34553243048391263,-0.2708298674538042,0,47.43192855600873,
			-0.037703249837783157,0.8609577587992641,0.15059552388459913,0,-36.96841498319127,
			0.24113635128153335,-0.07441037908422492,0.44972182064877153,0,-7.562075277591283,
			0,0,0,1,0];

var vintagePinhole = [0.6279345635605994,0.3202183420819367,-0.03965408211312453,0,9.651285835294123,
			0.02578397704808868,0.6441188644374771,0.03259127616149294,0,7.462829176470591,
			0.0466055556782719,-0.0851232987247891,0.5241648018700465,0,5.159190588235296,
			0,0,0,1,0];

var kodachrome = [1.1285582396593525,-0.3967382283601348,-0.03992559172921793,0,63.72958762196502,
			-0.16404339962244616,1.0835251566291304,-0.05498805115633132,0,24.732407896706203,
			-0.16786010706155763,-0.5603416277695248,1.6014850761964943,0,35.62982807460946,
			0,0,0,1,0];

var technicolor = [1.9125277891456083,-0.8545344976951645,-0.09155508482755585,0,11.793603434377337,
			-0.3087833385928097,1.7658908555458428,-0.10601743074722245,0,-70.35205161461398,
			-0.231103377548616,-0.7501899197440212,1.847597816108189,0,30.950940869491138,
			0,0,0,1,0];

var polaroid = [1.438,-0.062,-0.062,0,0,
			-0.122,1.378,-0.122,0,0,
			-0.016,-0.016,1.483,0,0,
			0,0,0,1,0];

function fillMatrix(src, dst) {
    for (var i = 0; i < 20; i++) {
            dst[i] = src[i];
    }
}
Caman.Filter.register("filter1910", function() {
    this.vintage();

    var canvas = this.canvas;
    var ctx = canvas.getContext('2d');
    var overlay = new Image();
    overlay.src = 'app/stylization/photo_style/instagram_filters/decorations/viewfinders/film-10.jpg';
    ctx.globalCompositeOperation = "multiply"
    ctx.drawImage(overlay, 0, 0, canvas.width, canvas.height);
    this.reloadCanvasData()

    return this.greyscale();

    });

Caman.Filter.register("filter1920", function() {
    this.clarity();

    var canvas = this.canvas;
    var ctx = canvas.getContext('2d');
    var overlay = new Image();
    overlay.src = 'app/stylization/photo_style/instagram_filters/decorations/viewfinders/film-20.jpg';
    ctx.globalCompositeOperation = "multiply"
    ctx.drawImage(overlay, 0, 0, canvas.width, canvas.height);
    this.reloadCanvasData()

    this.sepia(40);

    this.newLayer(function () {
        this.setBlendingMode('softLight');
        this.opacity(100);
        this.fillColor('#9c4210');
    });
    this.saturation(35);
    return this;
  });

   Caman.Filter.register("filter1930", function(grey) {
    this.hazyDays();
    return this.greyscale();
  });

    Caman.Filter.register("filter1970", function() {
    this.newLayer(function () {
    this.setBlendingMode('screen');
    this.opacity(30);
    this.fillColor('#f36abc');
    });
    this.contrast(10);
    this.brightness(10);
    this.saturation(30);

    return this;
    });

var filter1950 = function(img_path, out_path) {
    require('/opt/caffe/node_modules/node-easel');
    var image = new Image()
    image.src = img_path
    
    var canvas = new Canvas(image.width, image.height)
    var ctx = canvas.getContext('2d')

    var bitmap = new createjs.Bitmap(image)
    var matrix = new createjs.ColorMatrix()

    fillMatrix(kodachrome, matrix); // apply kodachrome color matrix

    var stage = new createjs.Stage(canvas);
    stage.addChild(bitmap)

    bitmap.filters = [new createjs.ColorMatrixFilter(matrix)]
    bitmap.cache(0, 0, image.width, image.height)
    stage.update()

    var fs = require('fs');
    fs.writeFile(out_path, canvas.toBuffer());
} 
var main = function () {
    if (process.argv.length == 5) {
       let img_path = process.argv[2]
       let decade = parseInt(process.argv[3])
       let out_path = process.argv[4]
       if (decade == 1950) {
            filter1950(img_path, out_path);
        }
        else {
        Caman(img_path, function () {
            switch (decade) {
            case 1910: this.filter1910(); break;
            case 1920: this.filter1920(); break;
            case 1930: this.filter1930(); break;
            case 1970: this.filter1970(); break;     
            } 
            this.render(function () {
             this.save(out_path);
          });
         });
        }
    }
} 
if (require.main === module) { 
    main(); 
}
