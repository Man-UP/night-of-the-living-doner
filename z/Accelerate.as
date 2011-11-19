package 
{
    import flash.display.Shape;
    import flash.display.Sprite;
    import flash.display.StageAlign;
    import flash.display.StageScaleMode;
    import flash.events.AccelerometerEvent;
	import flash.events.Event;
    import flash.geom.Matrix;
    import flash.sensors.Accelerometer;

	// This is the document class for the FLA
    public class Accelerate extends Sprite
    {
		private var background:Shape;
        private var ball:Sprite;
        private var accelerometer:Accelerometer;        
        private var xSpeed:Number = 0;
        private var ySpeed:Number = 0;
        private const RADIUS = 20;
        
        public function Accelerate()
        {
            stage.scaleMode = StageScaleMode.NO_SCALE;
            stage.align = StageAlign.TOP_LEFT;
            
			// draw the content (background and ball)
			createBackground();
            createBall();
            
			// check if the current platform supports accelerometer
            if (Accelerometer.isSupported)
            {
				// create the Accelerometer instance
                accelerometer = new Accelerometer();
				// register for the update event, which is dispatched at a regular interval
				// (it polls the sensor) and passes the current accelerometer values
                accelerometer.addEventListener(AccelerometerEvent.UPDATE, accUpdateHandler);
				// the enterFrame handler that's used to create the animation
				addEventListener(Event.ENTER_FRAME, enterFrameHandler);
            }
        }
        
		private function createBackground():void
		{
			background = new Shape();
			background.x = 0;
			background.y = 0;
			background.graphics.beginFill(0x0099FF);
			background.graphics.drawRect(0, 0, stage.stageWidth, stage.stageHeight);
			background.cacheAsBitmap = true;
			addChild(background);
		}
		
        private function createBall():void
        {
             ball = new Sprite();
             ball.graphics.beginFill(0x000044);
             ball.graphics.drawCircle(0, 0, RADIUS);
             ball.cacheAsBitmap;
             ball.x = stage.stageWidth / 2;
             ball.y = stage.stageHeight / 2;
             addChild(ball);
        }

		// this gets called when the accelerometer update is dispatched
        private function accUpdateHandler(event:AccelerometerEvent):void
        {
			// it simply adjusts the current "speed" according to the "acceleration"
			// based on the tilt of the device
            xSpeed += event.accelerationX * 2;
            ySpeed -= event.accelerationY * 2;
        }

		private function enterFrameHandler(event:Event):void
        {
            moveBall();
        }

        private function moveBall():void
        {
			// move the ball based on the current speed
            var newX:Number = ball.x + xSpeed;
            var newY:Number = ball.y + ySpeed;
			
			// this conditional just keeps the ball from leaving the screen
            if (newX < 20)
            {
                ball.x = RADIUS;
                xSpeed = 0;
            }
            else if (newX > stage.stageWidth - RADIUS)
            {
                ball.x = stage.stageWidth - RADIUS;
                xSpeed = 0;
            }
			// this is the normal case, if the ball isn't off screen
            else
            {
                ball.x += xSpeed;
            }
            
			// this conditional just keeps the ball from leaving the screen
            if (newY < RADIUS)
            {
                ball.y = RADIUS;
                ySpeed = 0;
            }
            else if (newY > stage.stageHeight - RADIUS)
            {
                ball.y = stage.stageHeight - RADIUS;
                ySpeed = 0;
            }
			// this is the normal case, if the ball isn't off screen
            else
            {
                ball.y += ySpeed;
            }
        }
    }
}