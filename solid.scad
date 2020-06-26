

difference(){
	rotate(a = [0, -30.8943255446, 0]) {
		rotate(a = [0, 0, 344.1176470588]) {
			translate(v = [13.6831495036, -48.0912821586, -58.8235294118]) {
				union() {
					translate(v = [-13.6831495036, 48.0912821586, 58.8235294118]) {
						rotate(a = [0, 30.8943255446, -344.1176470588]) {
							cube(center = true, size = [21.8185049322, 6, 20]);
						}
					}
				}
			}
		}
	}
	/* Holes Below*/
	rotate(a = [0, -30.8943255446, 0]){
		rotate(a = [0, 0, 344.1176470588]){
			translate(v = [13.6831495036, -48.0912821586, -58.8235294118]){
				union(){
					union() {
						translate(v = [4.6134179732, 49.7867088148, 47.0588235294]) {
							rotate(a = [0, 30.8943255446, -5.2941176471]) {
								union() {
									cube(center = true, size = [21.8185049322, 6, 20]);
									cube(center = true, size = [29.8185049322, 2, 9]);
								}
							}
						}
						translate(v = [0, 0, 47.0588235294]) {
							rotate(a = [0, 90, 84.7058823529]) {
								cylinder($fn = 32, center = true, h = 150, r = 5);
							}
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
						translate(v = [0, 0, 70.5882352941]) {
							rotate(a = [0, 90, -52.9411764706]) {
								cylinder($fn = 32, center = true, h = 150, r = 5);
							}
						}
					}
				}
			}
		}
	} /* End Holes */ 
}