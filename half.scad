

difference(){
	union() {
		translate(v = [0, 0, -3]) {
			cylinder($fn = 256, center = false, h = 15, r = 75);
		}
		translate(v = [46.6236114702, 18.0620833094, 11.7647058824]) {
			rotate(a = [0, 30.8943255446, -68.8235294118]) {
				cube(center = true, size = [21.8185049322, 6, 20]);
			}
		}
		translate(v = [-46.6236114702, -18.0620833094, 11.7647058824]) {
			rotate(a = [0, -30.8943255446, -68.8235294118]) {
				cube(center = true, size = [21.8185049322, 6, 20]);
			}
		}
		union() {
			translate(v = [36.9504458610, 33.6847821823, 23.5294117647]) {
				rotate(a = [0, 30.8943255446, -47.6470588235]) {
					union() {
						cube(center = true, size = [21.8185049322, 6, 20]);
						cube(center = true, size = [29.8185049322, 2, 9]);
					}
				}
			}
		}
		union() {
			translate(v = [-36.9504458610, -33.6847821823, 23.5294117647]) {
				rotate(a = [0, -30.8943255446, -47.6470588235]) {
					union() {
						cube(center = true, size = [21.8185049322, 6, 20]);
						cube(center = true, size = [29.8185049322, 2, 9]);
					}
				}
			}
		}
		translate(v = [22.2869177888, 44.7581645678, 35.2941176471]) {
			rotate(a = [0, 30.8943255446, -26.4705882353]) {
				cube(center = true, size = [21.8185049322, 6, 20]);
			}
		}
		translate(v = [-22.2869177888, -44.7581645678, 35.2941176471]) {
			rotate(a = [0, -30.8943255446, -26.4705882353]) {
				cube(center = true, size = [21.8185049322, 6, 20]);
			}
		}
		union() {
			translate(v = [4.6134179732, 49.7867088148, 47.0588235294]) {
				rotate(a = [0, 30.8943255446, -5.2941176471]) {
					union() {
						cube(center = true, size = [21.8185049322, 6, 20]);
						cube(center = true, size = [29.8185049322, 2, 9]);
					}
				}
			}
		}
		union() {
			translate(v = [-4.6134179732, -49.7867088148, 47.0588235294]) {
				rotate(a = [0, -30.8943255446, -5.2941176471]) {
					union() {
						cube(center = true, size = [21.8185049322, 6, 20]);
						cube(center = true, size = [29.8185049322, 2, 9]);
					}
				}
			}
		}
		translate(v = [-13.6831495036, 48.0912821586, 58.8235294118]) {
			rotate(a = [0, 30.8943255446, -344.1176470588]) {
				cube(center = true, size = [21.8185049322, 6, 20]);
			}
		}
		translate(v = [13.6831495036, -48.0912821586, 58.8235294118]) {
			rotate(a = [0, -30.8943255446, -344.1176470588]) {
				cube(center = true, size = [21.8185049322, 6, 20]);
			}
		}
		union() {
			translate(v = [-30.1317318190, 39.9008613640, 70.5882352941]) {
				rotate(a = [0, 30.8943255446, -322.9411764706]) {
					union() {
						cube(center = true, size = [21.8185049322, 6, 20]);
						cube(center = true, size = [29.8185049322, 2, 9]);
					}
				}
			}
		}
		union() {
			translate(v = [30.1317318190, -39.9008613640, 70.5882352941]) {
				rotate(a = [0, -30.8943255446, -322.9411764706]) {
					union() {
						cube(center = true, size = [21.8185049322, 6, 20]);
						cube(center = true, size = [29.8185049322, 2, 9]);
					}
				}
			}
		}
		translate(v = [-42.5108567865, 26.3216081439, 82.3529411765]) {
			rotate(a = [0, 30.8943255446, -301.7647058824]) {
				cube(center = true, size = [21.8185049322, 6, 20]);
			}
		}
		translate(v = [42.5108567865, -26.3216081439, 82.3529411765]) {
			rotate(a = [0, -30.8943255446, -301.7647058824]) {
				cube(center = true, size = [21.8185049322, 6, 20]);
			}
		}
		union() {
			translate(v = [-49.1486549842, 9.1874758908, 94.1176470588]) {
				rotate(a = [0, 30.8943255446, -280.5882352941]) {
					union() {
						cube(center = true, size = [21.8185049322, 6, 20]);
						cube(center = true, size = [29.3185049322, 1.5000000000, 8.5000000000]);
					}
				}
			}
		}
		union() {
			translate(v = [49.1486549842, -9.1874758908, 94.1176470588]) {
				rotate(a = [0, -30.8943255446, -280.5882352941]) {
					union() {
						cube(center = true, size = [21.8185049322, 6, 20]);
						cube(center = true, size = [29.3185049322, 1.5000000000, 8.5000000000]);
					}
				}
			}
		}
		translate(v = [-49.1486549842, -9.1874758908, 105.8823529412]) {
			rotate(a = [0, 30.8943255446, -259.4117647059]) {
				cube(center = true, size = [21.8185049322, 6, 20]);
			}
		}
	}
	/* Holes Below*/
	union(){
		union(){
			translate(v = [0, 0, 23.5294117647]) {
				rotate(a = [0, 90, 42.3529411765]) {
					cylinder($fn = 32, center = true, h = 150, r = 5);
				}
			}
		}
		union(){
			translate(v = [0, 0, 23.5294117647]) {
				rotate(a = [0, 90, 42.3529411765]) {
					cylinder($fn = 32, center = true, h = 150, r = 5);
				}
			}
		}
		union(){
			translate(v = [0, 0, 47.0588235294]) {
				rotate(a = [0, 90, 84.7058823529]) {
					cylinder($fn = 32, center = true, h = 150, r = 5);
				}
			}
		}
		union(){
			translate(v = [0, 0, 47.0588235294]) {
				rotate(a = [0, 90, 84.7058823529]) {
					cylinder($fn = 32, center = true, h = 150, r = 5);
				}
			}
		}
		union(){
			translate(v = [0, 0, 70.5882352941]) {
				rotate(a = [0, 90, -52.9411764706]) {
					cylinder($fn = 32, center = true, h = 150, r = 5);
				}
			}
		}
		union(){
			translate(v = [0, 0, 70.5882352941]) {
				rotate(a = [0, 90, -52.9411764706]) {
					cylinder($fn = 32, center = true, h = 150, r = 5);
				}
			}
		}
		union(){
			translate(v = [0, 0, 94.1176470588]) {
				rotate(a = [0, 90, -10.5882352941]) {
					cylinder($fn = 32, center = true, h = 150, r = 5);
				}
			}
		}
		union(){
			translate(v = [0, 0, 94.1176470588]) {
				rotate(a = [0, 90, -10.5882352941]) {
					cylinder($fn = 32, center = true, h = 150, r = 5);
				}
			}
		}
		union() {
			translate(v = [-42.5108567865, -26.3216081439, 117.6470588235]) {
				rotate(a = [0, 30.8943255446, -238.2352941176]) {
					union() {
						cube(center = true, size = [21.8185049322, 6, 20]);
						cube(center = true, size = [29.8185049322, 2, 9]);
					}
				}
			}
			translate(v = [0, 0, 117.6470588235]) {
				rotate(a = [0, 90, 31.7647058824]) {
					cylinder($fn = 32, center = true, h = 150, r = 5);
				}
			}
		}
	} /* End Holes */ 
}