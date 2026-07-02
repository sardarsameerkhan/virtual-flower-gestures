import cv2
import math

class InstagramFlower:
    def __init__(self):
        self.base_x = 0
        self.base_y = 0
        self.head_x = 0
        self.head_y = 0
        self.max_stem_length = 180  # Elegant, long stems
        
    def update_position(self, target_x, target_y, growth_progress):
        """Locks the stem base to a fingertip and shoots the flower head upwards."""
        self.base_x = target_x
        self.base_y = target_y
        
        # Calculate height purely based on the Grow hand's value
        self.head_x = self.base_x
        self.head_y = int(self.base_y - (self.max_stem_length * growth_progress))

    def draw(self, frame, growth_progress, bloom_progress):
        """Draws aesthetic neon-cyan stems and layered, glowing lotus petals."""
        
        # 1. Draw Sleek Cyan Stems (BGR: Electric Blue/Cyan)
        if growth_progress > 0.05:
            cv2.line(frame, (self.base_x, self.base_y), (self.head_x, self.head_y), (245, 170, 65), 3, cv2.LINE_AA)
            cv2.circle(frame, (self.base_x, self.base_y), 4, (245, 170, 65), -1)

        # 2. Draw Geometric Lotus Petals using Rotated Ellipses
        if growth_progress > 0.3 and bloom_progress > 0.05:
            num_petals = 6
            max_radius = int(38 * bloom_progress)
            
            # Layer 1: Outer Petals (Soft Pink-Coral)
            for i in range(num_petals):
                # Distribute angles symmetrically around a circle
                angle_deg = i * (360 / num_petals)
                angle_rad = math.radians(angle_deg)
                
                # Push the petal center slightly outward from the flower head core
                p_x = int(self.head_x + (max_radius * 0.4) * math.cos(angle_rad))
                p_y = int(self.head_y + (max_radius * 0.4) * math.sin(angle_rad))
                
                # Draw elegant pointed petals using ellipses
                # (frame, center, (axes), angle, startAngle, endAngle, color, thickness)
                cv2.ellipse(frame, (p_x, p_y), (int(max_radius * 0.6), int(max_radius * 0.3)), 
                            angle_deg, 0, 360, (110, 120, 245), -1, cv2.LINE_AA)
                
            # Layer 2: Inner Core Accent Petals (Warm Golden Orange)
            for i in range(num_petals):
                angle_deg = i * (360 / num_petals) + 30 # Offset angles to fill gaps
                angle_rad = math.radians(angle_deg)
                
                p_x = int(self.head_x + (max_radius * 0.2) * math.cos(angle_rad))
                p_y = int(self.head_y + (max_radius * 0.2) * math.sin(angle_rad))
                
                cv2.ellipse(frame, (p_x, p_y), (int(max_radius * 0.4), int(max_radius * 0.18)), 
                            angle_deg, 0, 360, (60, 185, 245), -1, cv2.LINE_AA)

            # Center golden pistil dome
            cv2.circle(frame, (self.head_x, self.head_y), int(max_radius * 0.22), (160, 240, 255), -1, cv2.LINE_AA)