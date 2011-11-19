/*
 * Title: Motion tracking with Flash and ActionScript 3
 * Web: http://www.richardsprojects.co.uk/post/motion-tracking-actionscript-3
 * Ref: Eg3
 * Copyright: Richard Garside, Jam Jar Collective
 * License: Creative Commons Attribution-Share Alike 2.0
 *
 * Inspired by and greatly helped by "THE ALMOST PERFECT FLASH 8 MOTION TRACKER"
 * By Yaniv Steiner - http://www.nastypixel.com/prototype/
 *
 * More details about The Jam Jar Collective
 * http://jamjarcollective.com
*/

package
{
	import flash.display.*;
	import flash.events.MouseEvent;
	import flash.events.TimerEvent;
	import flash.filters.*
	import flash.geom.*;
	import flash.media.Camera;
	import flash.ui.Mouse;
	import flash.utils.Timer;
	import fl.transitions.easing.None;
	import fl.transitions.Tween;
	
	public class MotionTracker extends MovieClip
	{
		private var m_boundingRect:Rectangle;
		private var m_computerCam:Camera;
		private var m_camShotBefore:BitmapData;
		private var m_camShotNow:BitmapData;
		private var m_colorForeground:uint;
		private var m_motionPreview:Bitmap;
		private var m_origin:Point;
		private var m_sizeDif:Number;
		private var m_points:Array;
		private var m_tweenX:Tween;
		private var m_tweenY:Tween;
		
		private var mcFollowText:MovieClip;
		private var screen1;
		private var update:Function;
		
		function MotionTracker(mc:MovieClip, screen:*, f:Function)
		{
			mcFollowText = mc;
			screen1 = screen;
			update = f;
			
			m_colorForeground = 0xffff0000;
			m_points = new Array();
			m_tweenX = new Tween(mcFollowText, "x", None.easeNone, mcFollowText.x, mcFollowText.x, 0.1, true);
			m_tweenY = new Tween(mcFollowText, "y", None.easeNone, mcFollowText.y, mcFollowText.y, 0.1, true);
			
			
		}
		
		/*
		 * 
		 */
		private function detection(ev:TimerEvent)
		{
	
			if (!m_computerCam.muted) {
				m_camShotNow.draw(screen1);
				
				// Highlight only the differences between before and now
				m_camShotNow.draw(m_camShotBefore, new Matrix(), new ColorTransform(), BlendMode.DIFFERENCE);
				m_camShotNow.threshold(m_camShotNow, m_boundingRect, m_origin, '>', 0xff333333, m_colorForeground);
				
				showPreview();
				m_camShotBefore.draw(screen1);

			 	// Work out where the differces are
				var re = m_camShotNow.getColorBoundsRect(0xffffffff, m_colorForeground, true);
				var colorChange =  m_camShotNow.threshold(m_camShotNow, re, new Point(re.x, re.y), '==', 0xffff0000, 0xffff0000);
				
				// Find the center of the differences if any detected
				if(colorChange > 10)
				{
					if (re.x<160)
					{
						var newY = (re.height / 2 + re.y) * m_sizeDif;
					}
					
					if (re.y<200)
					{
						trace(re.width, re.x, m_sizeDif);
						var newX = (re.width / 2 + re.x) * m_sizeDif;
						update(newX);
						//trace(newX);
					}
					
					// Move the following movie clip
					if(newX != undefined && newY != undefined)
					{
						// FIFO: First in, first out
						// Keep track of points used
						m_points.push(new Point(newX, newY));
						if(m_points.length > 2)
						{
							m_points.shift();
						}
						
						// Average the observed points to minimise error and sudden changes
						var averageX = 0;
						var averageY = 0;
						for each(var point:Point in m_points)
						{
							averageX += point.x;
							averageY += point.y;
						}
						
						// Tween to the next point to keep movement smooth
						m_tweenX.continueTo(newX, 0.1);
						m_tweenY.continueTo(newY, 0.1);
					}
				}
			}
		}
		
		
		/*
		 * Set everything up when user allows camera use
		 */
		public function init()
		{
			m_computerCam = Camera.getCamera();
			screen1.attachCamera(m_computerCam);
			
			m_camShotBefore = new BitmapData(m_computerCam.width, m_computerCam.height, false);
			m_camShotNow = new BitmapData(m_computerCam.width, m_computerCam.height, false);
			m_boundingRect = new Rectangle(0, 0, m_computerCam.width, m_computerCam.height);
			m_origin = new Point(0, 0);
			m_sizeDif = 960 / m_computerCam.width;
			
			var detectionTimer:Timer = new Timer(150);
            detectionTimer.addEventListener(TimerEvent.TIMER, detection);
            detectionTimer.start();
		}
		
		/*
		 * Show preview window of processed image
		 */
		private function showPreview()
		{
			m_motionPreview = new Bitmap(m_camShotNow);
			addChild(m_motionPreview);
		}
	}
}