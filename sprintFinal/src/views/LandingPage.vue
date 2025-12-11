<template>
  <div class="landing-page">
    <!-- Animated background effects -->
    <div class="bg-effects">
      <div class="glow-orb orb-1"></div>
      <div class="glow-orb orb-2"></div>
      <div class="glow-orb orb-3"></div>
    </div>

    <!-- Grid overlay -->
    <div class="grid-overlay"></div>

    <!-- Globe Background -->
    <div class="globe-container">
      <img src="/Users/preddy/Downloads/DV_PROJECT 2/src/assets/image.png" alt="Globe" class="globe-animation" />
    </div>

    <div class="content">
      <!-- Logo and Title -->
      <div class="header-section fade-in">
        <div class="logo">✈️</div>
        <h1>US Airport Delay Analysis Dashboard</h1>
        <div class="title-glow"></div>
      </div>
      
      <p class="subtitle fade-in" style="animation-delay: 0.1s;">
        Explore <span class="highlight">10 years</span> of comprehensive flight delay data integrated with 
        <span class="highlight">4,900+ customer reviews</span> to understand aviation performance across America
      </p>

      <div class="year-badge fade-in" style="animation-delay: 0.15s;">
        <span class="badge-glow"></span>
        2015 - 2025
      </div>

      <!-- Two Action Buttons -->
      <div class="action-buttons fade-in" style="animation-delay: 0.2s;">
        <button class="btn btn-explore" @click="showAbout = true">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M10 2C5.6 2 2 5.6 2 10s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8zm0 14c-3.3 0-6-2.7-6-6s2.7-6 6-6 6 2.7 6 6-2.7 6-6 6zm-1-9h2v2h-2V7zm0 4h2v4h-2v-4z" fill="currentColor"/>
          </svg>
          Explore More
        </button>
        
        <router-link to="/dashboard" class="btn btn-dashboard">
          <span>Explore Dashboard</span>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M7.5 15L12.5 10L7.5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </router-link>
      </div>

      <!-- Quick Stats -->
      <div class="stats-container fade-in" style="animation-delay: 0.3s;">
        <div class="stat-box">
          <div class="stat-icon">📅</div>
          <div class="stat-value">10</div>
          <div class="stat-label">Years</div>
        </div>
        <div class="stat-box">
          <div class="stat-icon">🛫</div>
          <div class="stat-value">200+</div>
          <div class="stat-label">Airports</div>
        </div>
        <div class="stat-box">
          <div class="stat-icon">✈️</div>
          <div class="stat-value">15+</div>
          <div class="stat-label">Airlines</div>
        </div>
        <div class="stat-box">
          <div class="stat-icon">⭐</div>
          <div class="stat-value">4.9K</div>
          <div class="stat-label">Reviews</div>
        </div>
      </div>

      <!-- Feature Highlights -->
      <div class="features fade-in" style="animation-delay: 0.4s;">
        <div class="feature-item">
          <span class="feature-icon">🗺️</span>
          <span>Interactive Maps</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">📊</span>
          <span>5 Chart Types</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">🔗</span>
          <span>Cross-Chart Filtering</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">💡</span>
          <span>Statistical Insights</span>
        </div>
      </div>

      <!-- Footer -->
      <div class="footer fade-in" style="animation-delay: 0.5s;">
        <p>Built with Vue.js + D3.js • Data from BTS & Skytrax</p>
      </div>
    </div>

    <!-- About Modal -->
    <transition name="modal-fade">
      <div v-if="showAbout" class="modal-overlay" @click="showAbout = false">
        <div class="modal-content" @click.stop>
          <button class="modal-close" @click="showAbout = false">×</button>
          
          <div class="modal-header">
            <span class="modal-icon">📊</span>
            <h2>About This Dashboard</h2>
          </div>

          <div class="modal-body">
            <div class="about-section">
              <h3>🎯 What You'll Discover</h3>
              <div class="about-grid">
                <div class="about-item">
                  <div class="about-item-icon">🗺️</div>
                  <div>
                    <strong>Geographic Insights</strong>
                    <p>Which states and airports face the most delays? Explore patterns across the US.</p>
                  </div>
                </div>
                <div class="about-item">
                  <div class="about-item-icon">📈</div>
                  <div>
                    <strong>Temporal Patterns</strong>
                    <p>How do delays vary by season and year? Identify peak periods and trends.</p>
                  </div>
                </div>
                <div class="about-item">
                  <div class="about-item-icon">✈️</div>
                  <div>
                    <strong>Airline Performance</strong>
                    <p>Compare carriers across multiple operational metrics and customer ratings.</p>
                  </div>
                </div>
                <div class="about-item">
                  <div class="about-item-icon">⭐</div>
                  <div>
                    <strong>Customer Sentiment</strong>
                    <p>Real passenger reviews reveal how delays impact satisfaction and loyalty.</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="about-section">
              <h3>🔬 Interactive Features</h3>
              <ul class="feature-list">
                <li><strong>5 Coordinated Visualizations:</strong> Choropleth Map, Sunburst Chart, Parallel Coordinates, Stream Graph, Bubble Chart</li>
                <li><strong>Cross-Chart Filtering:</strong> Click any element to filter all other charts instantly</li>
                <li><strong>Sentiment Analysis:</strong> 3 charts connecting operational delays to customer emotions</li>
                <li><strong>Time Range Control:</strong> Analyze any period from 2015-2025</li>
                <li><strong>Statistical Insights:</strong> Data-driven findings and recommendations</li>
              </ul>
            </div>

            <div class="about-section">
              <h3>📚 Data Sources</h3>
              <p class="data-info">
                <strong>Bureau of Transportation Statistics (BTS):</strong> Official flight delay and operational data from 200+ US airports and 15+ major carriers (2015-2025)
              </p>
              <p class="data-info">
                <strong>Skytrax Reviews:</strong> 4,900+ verified customer reviews with ratings across comfort, service, value, and overall satisfaction
              </p>
            </div>

            <div class="cta-section">
              <router-link to="/dashboard" class="modal-cta" @click="showAbout = false">
                Start Exploring →
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'LandingPage',
  setup() {
    const showAbout = ref(false)

    return {
      showAbout
    }
  }
}
</script>

<style scoped>
.landing-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0e27 0%, #16213e 50%, #0f3460 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 40px 20px;
}

/* Animated glowing orbs */
.bg-effects {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  animation: floatOrb 20s ease-in-out infinite;
}

.orb-1 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(0, 240, 255, 0.2), transparent 70%);
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.orb-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.15), transparent 70%);
  bottom: 10%;
  right: 10%;
  animation-delay: 7s;
}

.orb-3 {
  width: 350px;
  height: 350px;
  background: radial-gradient(circle, rgba(6, 182, 212, 0.12), transparent 70%);
  top: 50%;
  left: 50%;
  animation-delay: 14s;
}

@keyframes floatOrb {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(50px, -50px) scale(1.1); }
  50% { transform: translate(-30px, -80px) scale(0.9); }
  75% { transform: translate(40px, -30px) scale(1.05); }
}

/* Grid overlay effect */
.grid-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 240, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  pointer-events: none;
}

/* Globe Background */
.globe-container {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 800px;
  height: 800px;
  pointer-events: none;
  opacity: 0.08;
  z-index: 0;
}

.globe-animation {
  width: 100%;
  height: 100%;
  object-fit: contain;
  animation: rotateGlobe 40s linear infinite;
  filter: drop-shadow(0 0 30px rgba(0, 240, 255, 0.3));
}

@keyframes rotateGlobe {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Content */
.content {
  text-align: center;
  color: #e0e7ff;
  max-width: 900px;
  z-index: 1;
  position: relative;
}

/* Header Section */
.header-section {
  margin-bottom: 20px;
  position: relative;
}

.logo {
  font-size: 4.5rem;
  margin-bottom: 24px;
  display: inline-block;
  animation: pulse 3s ease-in-out infinite;
  filter: drop-shadow(0 0 20px rgba(0, 240, 255, 0.6));
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.9; }
}

h1 {
  font-size: 3.8rem;
  font-weight: 800;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #00f0ff 0%, #3b82f6 50%, #00f0ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -1.5px;
  line-height: 1.2;
  text-shadow: 0 0 40px rgba(0, 240, 255, 0.4);
  position: relative;
  animation: titleGlow 3s ease-in-out infinite;
}

@keyframes titleGlow {
  0%, 100% { filter: brightness(1); }
  50% { filter: brightness(1.2); }
}

.title-glow {
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  height: 3px;
  background: linear-gradient(90deg, transparent, #00f0ff, transparent);
  box-shadow: 0 0 20px #00f0ff;
}

.subtitle {
  font-size: 1.3rem;
  font-weight: 400;
  margin: 28px auto 24px;
  color: #cbd5e1;
  line-height: 1.8;
  max-width: 750px;
}

.subtitle .highlight {
  color: #00f0ff;
  font-weight: 700;
  text-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
}

.year-badge {
  display: inline-block;
  background: rgba(0, 240, 255, 0.1);
  border: 2px solid #00f0ff;
  color: #00f0ff;
  padding: 10px 28px;
  border-radius: 25px;
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 1px;
  margin: 16px 0 36px;
  box-shadow: 0 0 20px rgba(0, 240, 255, 0.3), inset 0 0 20px rgba(0, 240, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.badge-glow {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shine 3s infinite;
}

@keyframes shine {
  to { left: 100%; }
}

/* Action Buttons */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 50px;
  flex-wrap: wrap;
}

.btn {
  padding: 14px 32px;
  font-size: 1.05rem;
  font-weight: 700;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  position: relative;
  overflow: hidden;
  border: none;
  text-decoration: none;
}

.btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.btn:hover::before {
  width: 300px;
  height: 300px;
}

.btn-explore {
  background: transparent;
  border: 2px solid rgba(0, 240, 255, 0.6);
  color: #00f0ff;
  box-shadow: 0 0 20px rgba(0, 240, 255, 0.2);
}

.btn-explore:hover {
  background: rgba(0, 240, 255, 0.1);
  border-color: #00f0ff;
  box-shadow: 0 0 30px rgba(0, 240, 255, 0.4), inset 0 0 20px rgba(0, 240, 255, 0.1);
  transform: translateY(-2px);
}

.btn-dashboard {
  background: linear-gradient(135deg, #00f0ff 0%, #0ea5e9 100%);
  color: #0a0e27;
  box-shadow: 0 8px 25px rgba(0, 240, 255, 0.4);
}

.btn-dashboard:hover {
  box-shadow: 0 12px 35px rgba(0, 240, 255, 0.6);
  transform: translateY(-3px);
}

/* Stats Container */
.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 20px;
  max-width: 700px;
  margin: 0 auto 50px;
}

.stat-box {
  background: rgba(10, 14, 39, 0.6);
  border: 1px solid rgba(0, 240, 255, 0.3);
  border-radius: 16px;
  padding: 24px 16px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-box::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00f0ff, transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stat-box:hover {
  background: rgba(10, 14, 39, 0.8);
  border-color: #00f0ff;
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 240, 255, 0.3);
}

.stat-box:hover::before {
  opacity: 1;
}

.stat-icon {
  font-size: 2.5rem;
  margin-bottom: 12px;
  filter: drop-shadow(0 0 10px rgba(0, 240, 255, 0.5));
}

.stat-value {
  font-size: 2.2rem;
  font-weight: 800;
  color: #00f0ff;
  text-shadow: 0 0 20px rgba(0, 240, 255, 0.5);
  margin-bottom: 6px;
}

.stat-label {
  font-size: 0.8rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}

/* Features */
.features {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 50px;
}

.feature-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(10, 14, 39, 0.5);
  border: 1px solid rgba(0, 240, 255, 0.2);
  padding: 10px 20px;
  border-radius: 20px;
  font-size: 0.9rem;
  color: #cbd5e1;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.feature-item:hover {
  background: rgba(0, 240, 255, 0.1);
  border-color: #00f0ff;
  color: #00f0ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 240, 255, 0.3);
}

.feature-icon {
  font-size: 1.2rem;
  filter: drop-shadow(0 0 5px rgba(0, 240, 255, 0.5));
}

/* Footer */
.footer {
  margin-top: 60px;
  padding-top: 30px;
  border-top: 1px solid rgba(0, 240, 255, 0.2);
}

.footer p {
  font-size: 0.85rem;
  color: #64748b;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  backdrop-filter: blur(10px);
}

.modal-content {
  background: linear-gradient(135deg, rgba(10, 14, 39, 0.98), rgba(22, 33, 62, 0.98));
  border: 2px solid rgba(0, 240, 255, 0.4);
  border-radius: 24px;
  max-width: 850px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8), 0 0 40px rgba(0, 240, 255, 0.2);
  position: relative;
  animation: modalSlideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  backdrop-filter: blur(20px);
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-close {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.5);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-size: 1.8rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ef4444;
  transition: all 0.3s ease;
  z-index: 10;
}

.modal-close:hover {
  background: rgba(239, 68, 68, 0.3);
  transform: rotate(90deg);
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.5);
}

.modal-header {
  padding: 40px 40px 28px;
  border-bottom: 2px solid rgba(0, 240, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 16px;
}

.modal-icon {
  font-size: 3rem;
  filter: drop-shadow(0 0 15px rgba(0, 240, 255, 0.6));
}

.modal-header h2 {
  font-size: 2.2rem;
  font-weight: 800;
  color: #00f0ff;
  margin: 0;
  text-shadow: 0 0 20px rgba(0, 240, 255, 0.4);
}

.modal-body {
  padding: 40px;
}

.about-section {
  margin-bottom: 40px;
}

.about-section h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #00f0ff;
  margin-bottom: 24px;
  text-shadow: 0 0 15px rgba(0, 240, 255, 0.3);
}

.about-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.about-item {
  display: flex;
  gap: 14px;
  padding: 20px;
  background: rgba(10, 14, 39, 0.5);
  border-radius: 12px;
  border: 1px solid rgba(0, 240, 255, 0.2);
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.about-item:hover {
  border-color: rgba(0, 240, 255, 0.5);
  background: rgba(10, 14, 39, 0.7);
  box-shadow: 0 4px 20px rgba(0, 240, 255, 0.2);
}

.about-item-icon {
  font-size: 2.2rem;
  flex-shrink: 0;
  filter: drop-shadow(0 0 10px rgba(0, 240, 255, 0.5));
}

.about-item strong {
  display: block;
  font-weight: 700;
  color: #e0e7ff;
  margin-bottom: 6px;
  font-size: 1rem;
}

.about-item p {
  font-size: 0.9rem;
  color: #94a3b8;
  line-height: 1.6;
  margin: 0;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feature-list li {
  padding: 16px 20px;
  background: rgba(10, 14, 39, 0.5);
  border-radius: 10px;
  margin-bottom: 12px;
  border-left: 3px solid #00f0ff;
  font-size: 0.95rem;
  color: #cbd5e1;
  line-height: 1.7;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.feature-list li:hover {
  background: rgba(10, 14, 39, 0.7);
  box-shadow: 0 4px 15px rgba(0, 240, 255, 0.2);
  transform: translateX(4px);
}

.feature-list strong {
  color: #00f0ff;
  font-weight: 700;
}

.data-info {
  padding: 18px 20px;
  background: rgba(10, 14, 39, 0.5);
  border-radius: 10px;
  border: 1px solid rgba(0, 240, 255, 0.2);
  margin-bottom: 14px;
  font-size: 0.95rem;
  color: #cbd5e1;
  line-height: 1.7;
  backdrop-filter: blur(10px);
}

.data-info strong {
  color: #00f0ff;
  font-weight: 700;
  display: block;
  margin-bottom: 6px;
  text-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
}

.cta-section {
  text-align: center;
  margin-top: 36px;
  padding-top: 36px;
  border-top: 2px solid rgba(0, 240, 255, 0.2);
}

.modal-cta {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, #00f0ff 0%, #0ea5e9 100%);
  color: #0a0e27;
  padding: 16px 36px;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 800;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(0, 240, 255, 0.4);
}

.modal-cta:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(0, 240, 255, 0.6);
}

/* Animations */
.fade-in {
  animation: fadeInUp 0.8s ease-out forwards;
  opacity: 0;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-fade-enter-active, .modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from, .modal-fade-leave-to {
  opacity: 0;
}

/* Scrollbar */
.modal-content::-webkit-scrollbar {
  width: 8px;
}

.modal-content::-webkit-scrollbar-track {
  background: rgba(10, 14, 39, 0.5);
}

.modal-content::-webkit-scrollbar-thumb {
  background: rgba(0, 240, 255, 0.3);
  border-radius: 4px;
}

.modal-content::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 240, 255, 0.5);
}

/* Responsive */
@media (max-width: 768px) {
  .globe-container {
    width: 600px;
    height: 600px;
    opacity: 0.05;
  }

  h1 {
    font-size: 2.8rem;
  }

  .subtitle {
    font-size: 1.1rem;
  }

  .stats-container {
    grid-template-columns: repeat(2, 1fr);
    max-width: 400px;
  }

  .action-buttons {
    flex-direction: column;
    width: 100%;
    max-width: 320px;
    margin-left: auto;
    margin-right: auto;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .features {
    flex-direction: column;
    align-items: stretch;
    max-width: 320px;
    margin-left: auto;
    margin-right: auto;
  }

  .feature-item {
    justify-content: center;
  }

  .about-grid {
    grid-template-columns: 1fr;
  }

  .modal-body {
    padding: 28px;
  }

  .modal-header {
    padding: 32px 28px 24px;
  }
}

@media (max-width: 480px) {
  h1 {
    font-size: 2.2rem;
  }

  .logo {
    font-size: 3.5rem;
  }

  .stats-container {
    grid-template-columns: 1fr;
    max-width: 280px;
  }

  .modal-body {
    padding: 20px;
  }
}
</style>