

difference(){
	rotate(a = [90, 0, 0]) {
		rotate(a = [0, -30.8943255446, 0]) {
			rotate(a = [0, 0, 5.2941176471]) {
				translate(v = [-4.6134179732, -49.7867088148, -47.0588235294]) {
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
				}
			}
		}
	}
	/* Holes Below*/
	rotate(a = [90, 0, 0]){
		rotate(a = [0, -30.8943255446, 0]){
			rotate(a = [0, 0, 5.2941176471]){
				translate(v = [-4.6134179732, -49.7867088148, -47.0588235294]){
					union(){
						translate(v = [0, 0, 47.0588235294]) {
							rotate(a = [0, 90, 84.7058823529]) {
								cylinder($fn = 32, center = true, h = 150, r = 5);
							}
						}
					}
				}
			}
		}
	} /* End Holes */ 
}