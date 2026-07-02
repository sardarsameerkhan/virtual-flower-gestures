import cv2
import math
import os

class InstagramFlower:
    def __init__(self):
        self.base_x = 0
        self.base_y = 0
        self.head_x = 0
        self.head_y = 0
        self.max_stem_length = 200
        
        # Load the transparent asset images
        self.asset_bud = cv2.imread('assets/bud.png', cv2.IMREAD_UNCHANGED)
        self.asset_mid = cv2.imread('assets/mid.png', cv2.IMREAD_UNCHANGED)
        self.asset_full = cv2.imread('assets/full.png', cv2.IMREAD_UNCHANGED)
        
    def update_position(self, target_x, target_y, growth_progress):
        self.base_x = target_x
        self.base_y = target_y
        self.head_x = self.base_x
        self.head_y = int(self.base_y - (self.max_stem_length * growth_progress))

    def overlay_png(self, background, overlay, cx, cy, size):
        """Helper function to cleanly blend transparent PNG images over the webcam frame."""
        if overlay is None or size <= 0:
            return background
            
        # Resize the flower asset based on the current bloom scale
        img = cv2.resize(overlay, (size, size), interpolation=cv2.INTER_AREA)
        
        # Calculate bounding box coordinates
        x1, x2 = cx - size // 2, cx + size // 2
        y1, y2 = cy - size // 2, cy + size // 2
        
        # Ensure coordinates stay within the active screen frame
        h, w, _ = background.shape
        if x1 < 0 or y1 < 0 or x2 > w or y2 > h:
            return background

        # Isolate the color channels and the alpha transparency channel (4th channel)
        overlay_color = img[:, :, :3]
        mask = img[:, :, 3] / 255.0
        
        # Blend the overlay onto the background frame smoothly
        for c in range(0, 3):
            background[y1:y2, x1:x2, c] = (
                background[y1:y2, x1:x2, c] * (1.0 - mask) + 
                overlay_color[:, :, c] * mask
            )
        return background

    def draw(self, frame, growth_progress, bloom_progress):
        if growth_progress <= 0.05:
            return

        # 1. Draw Sleek Cyan Glowing Stem
        cv2.line(frame, (self.base_x, self.base_y), (self.head_x, self.head_y), (255, 230, 150), 4, cv2.LINE_AA)
        cv2.line(frame, (self.base_x, self.base_y), (self.head_x, self.head_y), (255, 150, 50), 2, cv2.LINE_AA)

        # 2. Render Shiny Real Asset designs based on active Bloom value
        if growth_progress > 0.4 and bloom_progress > 0.05:
            # Set absolute dynamic size bounds for the flower head
            flower_size = int(80 * bloom_progress)
            # Ensure size calculation is even to keep rendering math clean
            if flower_size % 2 != 0: flower_size += 1 
            
            # State machine tracking which asset to display based on your index finger spacing
            if bloom_progress < 0.4:
                # Early stage: Bud asset
                frame = self.overlay_png(frame, self.asset_bud, self.head_x, self.head_y, flower_size)
            elif bloom_progress < 0.75:
                # Middle stage: Semi-bloomed asset
                frame = self.overlay_png(frame, self.asset_mid, self.head_x, self.head_y, flower_size)
            else:
                # Maximum stage: Gorgeous fully opened glowing lotus asset
                frame = self.overlay_png(frame, self.asset_full, self.head_x, self.head_y, flower_size)