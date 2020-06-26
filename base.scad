

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
	}
	/* Holes Below*/
	union(){
		union() {
			translate(v = [36.9504458610, 33.6847821823, 23.5294117647]) {
				rotate(a = [0, 30.8943255446, -47.6470588235]) {
					union() {
						cube(center = true, size = [21.8185049322, 6, 20]);
						cube(center = true, size = [29.8185049322, 2, 9]);
					}
				}
			}
			translate(v = [0, 0, 23.5294117647]) {
				rotate(a = [0, 90, 42.3529411765]) {
					cylinder($fn = 32, center = true, h = 150, r = 5);
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
			translate(v = [0, 0, 23.5294117647]) {
				rotate(a = [0, 90, 42.3529411765]) {
					cylinder($fn = 32, center = true, h = 150, r = 5);
				}
			}
		}
	} /* End Holes */ 
}