# Virtual Lotus Bouquet AR Filter

An interactive, high-performance Augmented Reality (AR) computer vision application that generates an organic branching bouquet of glowing lotus flowers tracking a user's hands in real-time. Built with Python, OpenCV, and MediaPipe.

Inspired by premium TouchDesigner interactive spatial design installations, this filter utilizes asymmetric hand gestures to separately control the growth and blooming structures of a dense 15-flower cluster with natural physics.

## ✨ Key Features

* **Asymmetric Dual-Hand Control:**
    * **Left Hand (Grow):** Expanding your palm organically grows the branch stems up and outward from your wrist.
    * **Right Hand (Bloom):** Pinching/opening your thumb and index finger acts as a dial to bloom the flowers.
* **Dense Branching Architecture:** Automatically splits the tracking lines from 5 fingers into a beautiful bouquet of 15 overlapping sub-branches.
* **Dynamic Color Shifting:** As the bouquet blooms, the colors smoothly transition across a vibrant HSV color gradient.
* **Natural Physics Sway:** Built-in inertia lag calculation makes the flower heads tilt and sway organically when you wave your hand.
* **Pollen Particle Explosions:** Hitting a 100% bloom triggers a burst of golden, floating pollen particles drifting upward from the petals.
* **Lag-Free Performance:** Uses NumPy parallel matrix operations and alpha-channel image caching to maintain a smooth 30+ FPS.

---

## 🛠️ Tech Stack

* **Language:** Python 3
* **Computer Vision:** OpenCV (`opencv-python`)
* **Hand Tracking:** Google MediaPipe
* **Data Processing:** NumPy

---

## 📦 Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/sardarsameerkhan/virtual-flower-gestures.git](https://github.com/sardarsameerkhan/virtual-flower-gestures)
cd https://github.com/sardarsameerkhan/virtual-flower-gestures