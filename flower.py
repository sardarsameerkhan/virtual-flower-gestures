import cv2
import math

class VirtualFlower:
    def __init__(self):
        # Coordinates for the base of the stem and the top flower head
        self.base_x = 0
        self.base_y = 0
        self.head_x = 0
        self.head_y = 0
        
        # Growth and Bloom stages tracked from 0.0 (closed/seed) to 1.0 (fully open)
        self.growth_progress = 0.0
        self.bloom_progress = 0.0
        
        # Max height the stem grows upwards (in pixels)
        self.max_stem_length = 120
        
    def update(self, target_x, target_y, is_hand_open, open_ratio):
        """Updates the growth and bloom values dynamically based on hand state."""
        self.base_x = target_x
        self.base_y = target_y
        
        if is_hand_open:
            # Grow the stem upwards first
            if self.growth_progress < 1.0:
                self.growth_progress += 0.08  # Speed of stem growth
            else:
                # Once grown, bloom the petals matching how wide the hand is open
                self.bloom_progress = min(1.0, open_ratio)
        else:
            # If the hand closes, shrink everything back down smoothly
            if self.bloom_progress > 0.0:
                self.bloom_progress -= 0.1
            elif self.growth_progress > 0.0:
                self.growth_progress -= 0.08

        # Calculate where the flower top sits based on current growth
        self.head_x = self.base_x
        self.head_y = int(self.base_y - (self.max_stem_length * self.growth_progress))

    def draw(self, frame):
        """Draws the glowing stem and lotus petals on the camera feed."""
        if self.growth_progress > 0.0:
            # 1. Draw the Neon Blue/Cyan Stem (like the Instagram image)
            cv2.line(frame, (self.base_x, self.base_y), (self.head_x, self.head_y), (255, 180, 50), 3)
            
        if self.bloom_progress > 0.0:
            # 2. Draw 6 overlapping bright Coral/Red Petals radiating from the head
            num_petals = 6
            max_radius = int(35 * self.bloom_progress)
            
            for i in range(num_petals):
                angle = i * (2 * math.pi / num_petals)
                petal_x = int(self.head_x + (max_radius * 0.5) * math.cos(angle))
                petal_y = int(self.head_y + (max_radius * 0.5) * math.sin(angle))
                
                # Outer soft translucent petal layer
                cv2.circle(frame, (petal_x, petal_y), int(max_radius * 0.6), (100, 100, 255), -1)
            
            # Draw a bright center core for the lotus bloom
            cv2.circle(frame, (self.head_x, self.head_y), int(max_radius * 0.3), (200, 230, 255), -1)
            
            # Add the text status layout mimicking your reference photo
            cv2.putText(frame, f"Bloom: {self.bloom_progress:.2f}", (self.head_x + 15, self.head_y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (240, 160, 120), 1, cv2.LINE_AA)