<template>
  <div class="landing-page">
    <!-- Animated background -->
    <div class="bg-gradient"></div>
    <div class="grid-overlay"></div>
    
    <!-- Globe animation -->
    <div class="globe-container">
      <img src="../assets/image.png" alt="Globe" class="globe-animation" />
    </div>

    <!-- Floating airplanes -->
    <div class="airplane airplane-1">✈️</div>
    <div class="airplane airplane-2">✈️</div>
    <div class="airplane airplane-3">✈️</div>

    <div class="content">
      <!-- Main heading -->
      <div class="title-section fade-in">
        <h1>US Airport Delay Analysis</h1>
        <div class="title-underline"></div>
      </div>
      
      <p class="subtitle fade-in" style="animation-delay: 0.2s;">
        A comprehensive 10-year analysis of flight delays across America
        <span class="year-range">(2015-2025)</span>
      </p>

      <!-- Stats cards -->
      <div class="stats-grid">
        <div class="stat-card fade-in" style="animation-delay: 0.3s;">
          <div class="stat-icon">📅</div>
          <div class="stat-number">10</div>
          <div class="stat-label">Years of Data</div>
        </div>
        <div class="stat-card fade-in" style="animation-delay: 0.4s;">
          <div class="stat-icon">✈️</div>
          <div class="stat-number">200+</div>
          <div class="stat-label">Airports Analyzed</div>
        </div>
        <div class="stat-card fade-in" style="animation-delay: 0.5s;">
          <div class="stat-icon">⭐</div>
          <div class="stat-number">4.9K</div>
          <div class="stat-label">Reviews Analyzed</div>
        </div>
      </div>

      <!-- CTA Button -->
      <router-link to="/dashboard" class="cta-button fade-in" style="animation-delay: 0.6s;">
        <span>Start Exploring</span>
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M7.5 15L12.5 10L7.5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </router-link>

      <!-- Feature tags -->
      <div class="features-grid">
        <div class="feature-tag fade-in" style="animation-delay: 0.7s;">
          <span class="feature-icon">📊</span>
          <span>Interactive Visualizations</span>
        </div>
        <div class="feature-tag fade-in" style="animation-delay: 0.8s;">
          <span class="feature-icon">🗺️</span>
          <span>Geographic Analysis</span>
        </div>
        <div class="feature-tag fade-in" style="animation-delay: 0.9s;">
          <span class="feature-icon">📈</span>
          <span>Temporal Trends</span>
        </div>
        <div class="feature-tag fade-in" style="animation-delay: 1.0s;">
          <span class="feature-icon">🎯</span>
          <span>Airline Comparison</span>
        </div>
        <div class="feature-tag fade-in" style="animation-delay: 1.1s;">
          <span class="feature-icon">💡</span>
          <span>Data-Driven Insights</span>
        </div>
      </div>

    
    </div>
  </div>
</template>

<script>
export default {
  name: 'LandingPage',
  mounted() {
    console.log('Landing page mounted')
  }
}
</script>

<style scoped>
.landing-page {
  min-height: 100vh;
  background: #0a0a0a;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

/* Background effects */
.bg-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(ellipse at 15% 20%, rgba(102, 126, 234, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 85% 80%, rgba(118, 75, 162, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 50%, rgba(102, 126, 234, 0.08) 0%, transparent 60%);
  pointer-events: none;
}

.grid-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 50px 50px;
  pointer-events: none;
  opacity: 0.5;
}

/* Globe animation - Full background */
.globe-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  opacity: 0.3;
  z-index: 0;
}

.globe-animation {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Floating airplanes */
.airplane {
  position: absolute;
  font-size: 2rem;
  opacity: 0.1;
  filter: grayscale(100%);
  pointer-events: none;
}

.airplane-1 {
  top: 15%;
  left: -80px;
  animation: fly1 30s linear infinite;
}

.airplane-2 {
  top: 55%;
  left: -80px;
  animation: fly2 35s linear infinite 5s;
}

.airplane-3 {
  top: 78%;
  left: -80px;
  animation: fly3 28s linear infinite 10s;
}

@keyframes fly1 {
  0% {
    transform: translateX(-80px) translateY(0) rotate(45deg);
  }
  100% {
    transform: translateX(calc(100vw + 80px)) translateY(-15vh) rotate(45deg);
  }
}

@keyframes fly2 {
  0% {
    transform: translateX(-80px) translateY(0) rotate(40deg);
  }
  100% {
    transform: translateX(calc(100vw + 80px)) translateY(-25vh) rotate(40deg);
  }
}

@keyframes fly3 {
  0% {
    transform: translateX(-80px) translateY(0) rotate(50deg);
  }
  100% {
    transform: translateX(calc(100vw + 80px)) translateY(-20vh) rotate(50deg);
  }
}

/* Content */
.content {
  text-align: center;
  color: white;
  padding: 40px;
  max-width: 1000px;
  z-index: 1;
  position: relative;
}

/* Title section */
.title-section {
  margin-bottom: 15px;
}

h1 {
  font-size: 4rem;
  font-weight: 800;
  margin-bottom: 15px;
  background: linear-gradient(135deg, #ffffff 0%, #667eea 50%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -2px;
  line-height: 1.1;
}

.title-underline {
  width: 120px;
  height: 4px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  margin: 0 auto;
  border-radius: 2px;
}

.subtitle {
  font-size: 1.25rem;
  font-weight: 300;
  margin-bottom: 50px;
  color: #b0b0b0;
  line-height: 1.6;
}

.year-range {
  display: block;
  margin-top: 5px;
  font-size: 1rem;
  color: #808080;
}

/* Stats grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 25px;
  margin: 0 auto 50px;
  max-width: 800px;
}

.stat-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 30px 20px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  opacity: 0;
  transition: opacity 0.3s;
}

.stat-card:hover {
  transform: translateY(-8px);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%);
  border-color: rgba(102, 126, 234, 0.4);
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-icon {
  font-size: 2.5rem;
  margin-bottom: 12px;
  filter: grayscale(30%);
}

.stat-number {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 0.9rem;
  color: #808080;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  font-weight: 500;
}

/* CTA Button */
.cta-button {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 18px 40px;
  font-size: 1.15rem;
  font-weight: 600;
  text-decoration: none;
  border-radius: 50px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
  border: 2px solid transparent;
  position: relative;
  overflow: hidden;
}

.cta-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.6s;
}

.cta-button:hover::before {
  left: 100%;
}

.cta-button:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 15px 50px rgba(102, 126, 234, 0.5);
  border-color: rgba(255, 255, 255, 0.3);
}

.cta-button svg {
  transition: transform 0.3s;
}

.cta-button:hover svg {
  transform: translateX(5px);
}

/* Features grid */
.features-grid {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 60px;
  margin-bottom: 40px;
}

.feature-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 10px 20px;
  border-radius: 30px;
  font-size: 0.9rem;
  color: #b0b0b0;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

.feature-tag:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(102, 126, 234, 0.4);
  color: white;
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 1.1rem;
}

/* Scroll indicator */
.scroll-indicator {
  margin-top: 50px;
  opacity: 0.5;
}

.scroll-text {
  font-size: 0.85rem;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 2px;
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

/* Responsive */
@media (max-width: 768px) {
  .globe-container {
    opacity: 0.2;
  }

  h1 {
    font-size: 2.5rem;
    letter-spacing: -1px;
  }

  .subtitle {
    font-size: 1rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: 15px;
    max-width: 300px;
  }

  .stat-card {
    padding: 25px 15px;
  }

  .stat-number {
    font-size: 2.5rem;
  }

  .stat-icon {
    font-size: 2rem;
  }

  .cta-button {
    padding: 16px 35px;
    font-size: 1rem;
  }

  .features-grid {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .feature-tag {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  h1 {
    font-size: 2rem;
  }

  .globe-container {
    opacity: 0.15;
  }
}
</style>