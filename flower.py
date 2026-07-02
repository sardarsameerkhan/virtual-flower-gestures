import cv2
import math

class InstagramFlower:
    def __init__(self):
        self.base_x = 0
        self.base_y = 0
        self.head_x = 0
        self.head_y = 0
        self.max_stem_length = 200  # Length of the long stems
        
        # Load alpha-channel transparent asset pictures
        self.asset_bud = cv2.imread('assets/bud.png', cv2.IMREAD_UNCHANGED)
        self.asset_mid = cv2.imread('assets/mid.png', cv2.IMREAD_UNCHANGED)
        self.asset_full = cv2.imread('assets/full.png', cv2.IMREAD_UNCHANGED)
        
    def update_position(self, target_x, target_y, growth_progress):
        """Locks the stem base to a fingertip and calculates height based on growth."""
        self.base_x = target_x
        self.base_y = target_y
        
        # Calculate where the flower head is relative to current growth progress
        self.head_x = self.base_x
        self.head_y = int(self.base_y - (self.max_stem_length * growth_progress))

    def overlay_png(self, background, overlay, cx, cy, size):
        """Safely blends alpha-transparent PNG assets onto the camera frame."""
        if overlay is None or size <= 0:
            return background
            
        # Dynamically scale the image based on user gesture ratios
        img = cv2.resize(overlay, (size, size), interpolation=cv2.INTER_AREA)
        
        # Define pixel boundary boxes
        x1, x2 = cx - size // 2, cx + size // 2
        y1, y2 = cy - size // 2, cy + size // 2
        
        # Edge protection: Keep rendering within webcam resolution space
        h, w, _ = background.shape
        if x1 < 0 or y1 < 0 or x2 > w or y2 > h:
            return background

        # Splitting color array channels from transparency layer map
        overlay_color = img[:, :, :3]
        mask = img[:, :, 3] / 255.0
        
        # Apply matrix cross-blending weights
        for c in range(0, 3):
            background[y1:y2, x1:x2, c] = (
                background[y1:y2, x1:x2, c] * (1.0 - mask) + 
                overlay_color[:, :, c] * mask
            )
        return background

    def draw(self, frame, growth_progress, bloom_progress):
        """Draws the glowing stems and crossfades the active image asset."""
        if growth_progress <= 0.05:
            return

        # 1. Render Cyan Glowing Stems (Double line overlay for glow effect)
        cv2.line(frame, (self.base_x, self.base_y), (self.head_x, self.head_y), (255, 230, 150), 4, cv2.LINE_AA)
        cv2.line(frame, (self.base_x, self.base_y), (self.head_x, self.head_y), (255, 150, 50), 2, cv2.LINE_AA)

        # 2. Render PNG Asset stages driven by bloom control values
        if growth_progress > 0.4 and bloom_progress > 0.05:
            flower_size = int(90 * bloom_progress)
            if flower_size % 2 != 0: 
                flower_size += 1 
            
            # Decide which image design stage to overlay based on proximity
            if bloom_progress < 0.4:
                frame = self.overlay_png(frame, self.asset_bud, self.head_x, self.head_y, flower_size)
            elif bloom_progress < 0.75:
                frame = self.overlay_png(frame, self.asset_mid, self.head_x, self.head_y, flower_size)
            else:
                frame = self.overlay_png(frame, self.asset_full, self.head_x, self.head_y, flower_size)