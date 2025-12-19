# 🔍 Circuit Sherlock  
### AI-Powered PCB Defect Detection System

Circuit Sherlock is an AI-powered computer vision system designed to automatically detect defects in **bare Printed Circuit Boards (PCBs)** using **YOLO** and a **Flask-based web interface**. The system supports image uploads and live video inspection to improve speed, accuracy, and efficiency in manufacturing quality control.

---

## 📌 Overview
In the manufacturing industry, manual PCB inspection is time-consuming and error-prone. Circuit Sherlock leverages deep learning to identify PCB defects in real time, providing a scalable and accessible solution for automated quality assurance.

---

## 🎯 Objective
To design and deploy an AI-powered PCB defect detection system that:
- Detects defects accurately using YOLO
- Supports real-time inspection via webcam
- Provides a user-friendly web interface
- Improves inspection speed and reliability for PCB manufacturers

---

## 🧠 Defects Detected
- Missing Hole  
- Mouse Bite  
- Open Circuit  
- Short Circuit  
- Spurious Copper  
- Spur  

---

## 🛠️ Tech Stack

### Programming & Frameworks
- **Python**
- **JavaScript**
- **Flask** (Backend)
- **YOLO (Ultralytics – YOLOv8 / YOLO11n)**

### Frontend
- HTML5  
- CSS3  
- Bootstrap  

### Data Science & Visualization
- OpenCV  
- NumPy  
- Pandas  
- Matplotlib  

### Tools & Platforms
- Kaggle (GPU training)
- Jupyter Notebook
- VS Code

---

## 📂 Dataset Description
- High-resolution bare PCB images
- Both defect-free and defective samples
- Annotated with bounding boxes and defect labels
- Includes real-world and augmented images
- Supports image-based and live video detection

---

## ⚙️ Model Training Details
- **YOLO Version:** YOLO11n  
- **Training Images:** 6,370  
- **Validation Images:** 802  
- **Input Size:** 640 × 640  

---

## 🔄 Workflow
1. User uploads a PCB image or starts live webcam feed
2. Flask backend receives input
3. YOLO model performs defect detection
4. Detected defects are highlighted with bounding boxes
5. Results are displayed on the web interface in real time

---

## 🌐 Full Stack & AI Integration
Flask acts as the bridge between the frontend and the YOLO detection model. It efficiently handles:
- Image uploads
- Live camera frames
- Model inference
- Result visualization

This lightweight architecture ensures smooth communication between UI and AI engine.

---

## ⚠️ Limitations
- Live webcam preview may lag on low-end devices
- Large YOLO model size makes deployment challenging
- Free cloud platforms have memory and storage constraints
- UI performance depends on user hardware

---

## 🚀 Future Scope
- Integration with industrial-grade high-resolution cameras
- Automated defect reports and production analytics
- Support for multi-layer and assembled PCBs
- Cloud-based scalable deployment

---

## ✅ Conclusion
Circuit Sherlock demonstrates how AI can transform PCB quality control through real-time defect detection. By combining YOLO with a clean web interface, the system delivers fast, accurate, and automated inspection—laying a strong foundation for industrial automation.

---

## 👤 Author
**Bharath Kumar**  
B.Tech Final Year | Machine Learning & Full Stack Enthusiast  

---

## 👥 Team & Contributors
### 📊 Data Science
- Bharath Kumar Barre  
- Ravi Kumar Penumajji  
- Varsha Bandari  
### 🌐 Full Stack Development
- Satya Saiesh Munjuluri  
- Sai Surya Chekuri  
- Maneesha Pulakanti  

---

## ⭐ Acknowledgements
- Ultralytics YOLO
- OpenCV Community
- Flask Framework
- Kaggle
