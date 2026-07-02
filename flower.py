import cv2
import math

class InstagramFlower:
    def __init__(self):
        self.base_x = 0
        self.base_y = 0
        self.head_x = 0
        self.head_y = 0
        self.max_stem_length = 200  # Longer, elegant stems like the reel
        
    def update_position(self, target_x, target_y, growth_progress):
        """Locks the flower to the finger tip and calculates its height based on the growth hand."""
        self.base_x = target_x
        self.base_y = target_y
        
        # Stems grow strictly upwards
        self.head_x = self.base_x
        self.head_y = int(self.base_y - (self.max_stem_length * growth_progress))

    def draw(self, frame, growth_progress, bloom_progress):
        """Draws the high-fidelity aesthetic flowers and stems."""
        
        # 1. Draw the sleek Neon Blue Stem (BGR: Blue=255, Green=100, Red=0)
        if growth_progress > 0.05:
            # Main stem line
            cv2.line(frame, (self.base_x, self.base_y), (self.head_x, self.head_y), (255, 120, 30), 4, cv2.LINE_AA)
            # Small glowing base connector node
            cv2.circle(frame, (self.base_x, self.base_y), 5, (255, 200, 100), -1)

        # 2. Draw the Vibrant Coral/Pink Lotus Petals
        if growth_progress > 0.5 and bloom_progress > 0.05:
            num_petals = 8  # More petals for a fuller look
            max_radius = int(50 * bloom_progress)
            
            # Layer 1: Outer dark pink/coral petals
            for i in range(num_petals):
                angle = i * (2 * math.pi / num_petals) - (math.pi / 2)  # Orient upright
                # Make petals slightly elliptical/pointed upwards
                p_x = int(self.head_x + (max_radius * 0.7) * math.cos(angle))
                p_y = int(self.head_y + (max_radius * 0.9) * math.sin(angle))
                
                # Draw sharp petal vectors (BGR: Soft bright red/pink)
                cv2.circle(frame, (p_x, p_y), int(max_radius * 0.5), (120, 100, 255), -1, cv2.LINE_AA)
            
            # Layer 2: Inner glowing orange/gold core petals
            for i in range(num_petals):
                angle = i * (2 * math.pi / num_petals) + 0.3 # Offset angle for interlayering
                p_x = int(self.head_x + (max_radius * 0.4) * math.cos(angle))
                p_y = int(self.head_y + (max_radius * 0.5) * math.sin(angle))
                cv2.circle(frame, (p_x, p_y), int(max_radius * 0.3), (80, 180, 255), -1, cv2.LINE_AA)

            # Center golden pistil node
            cv2.circle(frame, (self.head_x, self.head_y), int(max_radius * 0.2), (180, 240, 255), -1, cv2.LINE_AA)