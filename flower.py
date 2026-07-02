import cv2
import math
import numpy as np

class InstagramFlower:
    def __init__(self):
        self.base_x = 0
        self.base_y = 0
        self.head_x = 0
        self.head_y = 0
        self.max_stem_length = 200
        
    def update_position(self, target_x, target_y, growth_progress):
        self.base_x = target_x
        self.base_y = target_y
        self.head_x = self.base_x
        self.head_y = int(self.base_y - (self.max_stem_length * growth_progress))

    def draw(self, frame, growth_progress, bloom_progress):
        if growth_progress <= 0.05:
            return

        # 1. Draw Sleek Cyan Stem with a subtle double-line to look "glowing"
        cv2.line(frame, (self.base_x, self.base_y), (self.head_x, self.head_y), (255, 230, 150), 5, cv2.LINE_AA)
        cv2.line(frame, (self.base_x, self.base_y), (self.head_x, self.head_y), (255, 150, 50), 2, cv2.LINE_AA)
        cv2.circle(frame, (self.base_x, self.base_y), 5, (255, 170, 50), -1)

        # 2. Draw Premium Realistic Multi-layered Lotus
        if growth_progress > 0.3 and bloom_progress > 0.05:
            max_radius = int(45 * bloom_progress)
            
            # Layer 1: Outer Pointed Petals (Deep Coral/Pink)
            self._draw_pointed_petals(frame, self.head_x, self.head_y, max_radius, 8, 1.0, (120, 100, 255))
            
            # Layer 2: Middle Petals (Bright Soft Rose - Offset for realism)
            self._draw_pointed_petals(frame, self.head_x, self.head_y, int(max_radius * 0.8), 6, 0.8, (160, 140, 255), angle_offset=30)
            
            # Layer 3: Inner Golden Accent Petals (Provides that "shiny/glowing" depth)
            self._draw_pointed_petals(frame, self.head_x, self.head_y, int(max_radius * 0.5), 5, 0.6, (80, 200, 255))

            # Center Pistil Bulb (Glowing white-yellow core)
            cv2.circle(frame, (self.head_x, self.head_y), int(max_radius * 0.2), (200, 245, 255), -1, cv2.LINE_AA)

    def _draw_pointed_petals(self, frame, cx, cy, radius, num_petals, aspect, color, angle_offset=0):
        """Helper to draw realistic pointed lotus petals using mathematical vector paths."""
        for i in range(num_petals):
            angle_deg = i * (360 / num_petals) + angle_offset
            angle_rad = math.radians(angle_deg)
            
            # Top tip point of the petal
            tip_x = int(cx + radius * math.cos(angle_rad))
            tip_y = int(cy + (radius * aspect) * math.sin(angle_rad))
            
            # Base left and right sides of the petal to create a sharp diamond/leaf look
            side1_angle = math.radians(angle_deg - 20)
            side2_angle = math.radians(angle_deg + 20)
            
            s1_x = int(cx + (radius * 0.4) * math.cos(side1_angle))
            s1_y = int(cy + (radius * 0.4 * aspect) * math.sin(side1_angle))
            
            s2_x = int(cx + (radius * 0.4) * math.cos(side2_angle))
            s2_y = int(cy + (radius * 0.4 * aspect) * math.sin(side2_angle))
            
            # Construct the polygon path and draw it smoothly
            pts = np.array([[cx, cy], [s1_x, s1_y], [tip_x, tip_y], [s2_x, s2_y]], np.int32)
            cv2.fillPoly(frame, [pts], color, lineType=cv2.LINE_AA)