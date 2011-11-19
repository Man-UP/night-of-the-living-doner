package  {
	
	import flash.display.Bitmap;
	import flash.display.Sprite;
	
	public class Vehicle extends Sprite {
		
		public var laneNumber:int;
		private var vehicleBitmap:Bitmap;
		
		public function Vehicle(lane:int, bitmap:Bitmap) {
			// constructor code
			laneNumber = lane;
			vehicleBitmap = bitmap;
		}
		
		public function showVehicle() {
			switch (laneNumber) {
				case 1: 
					addChild(vehicleBitmap);
					this.x = 196.45 * 2;
					this.y = 150 * 2;
					this.width = 36 * 2;
					this.height = 24 * 2;	break;
				case 2:
					addChild(vehicleBitmap);
					this.x = 222.05 * 2;
					this.y = 145.55 * 2;
					this.width = 36.55 * 2;
					this.height = 24.45 * 2;	break;
				case 3: 
					addChild(vehicleBitmap);
					this.x = 243.45 * 2;
					this.y = 153.7 * 2;
					this.width = 35 * 2;
					this.height = 23.3 * 2;	break;
				default: break;
			}
		}
		
		public function moveVehicle() {
			switch (laneNumber) {
				case 1: 
					this.x -= 17.25;
					this.y += 1.85;
					this.width += 17.17;
					this.height += 11.45;	break;
				case 2:
					this.x -= 7.9;
					this.y += 1.85;
					this.width += 16;
					this.height += 10.6;	break;
				case 3:
					this.x += 1.83;
					this.y += 2.4;
					this.width += 17.17;
					this.height += 11.45;	break;
				default: break;
			}
		}

	}
	
}
