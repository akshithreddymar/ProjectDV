<template>
  <div class="landing-page">
    <!-- Animated background elements -->
    <div class="bg-gradient"></div>
    <div class="airplane" style="top: 10%; left: -100px;">✈️</div>
    <div class="airplane" style="top: 50%; left: -100px; animation-delay: 8s;">✈️</div>
    <div class="airplane" style="top: 80%; left: -100px; animation-delay: 16s;">✈️</div>

    <div class="content">
      <h1 class="fade-in">US Airport Delay Analysis</h1>
      <p class="subtitle fade-in">A comprehensive 10-year analysis of flight delays across America (2015-2025)</p>

      <div class="stats">
        <div class="stat-box fade-in" style="animation-delay: 0.2s;">
          <span class="stat-number">10</span>
          <span class="stat-label">Years of Data</span>
        </div>
        <div class="stat-box fade-in" style="animation-delay: 0.3s;">
          <span class="stat-number">200+</span>
          <span class="stat-label">Airports</span>
        </div>
        <div class="stat-box fade-in" style="animation-delay: 0.4s;">
          <span class="stat-number">4.9K</span>
          <span class="stat-label">Reviews Analyzed</span>
        </div>
      </div>

      <router-link to="/dashboard" class="cta-button fade-in" style="animation-delay: 0.5s;">
        Start Exploring →
      </router-link>

      <div class="features">
        <div class="feature fade-in" style="animation-delay: 0.6s;">📊 Interactive Visualizations</div>
        <div class="feature fade-in" style="animation-delay: 0.7s;">🗺️ Geographic Analysis</div>
        <div class="feature fade-in" style="animation-delay: 0.8s;">✈️ Airline Comparison</div>
        <div class="feature fade-in" style="animation-delay: 0.9s;">📈 Temporal Trends</div>
        <div class="feature fade-in" style="animation-delay: 1.0s;">💬 Customer Sentiment</div>
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
  background: #1a1a1a;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.bg-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(ellipse at 20% 20%, rgba(102, 126, 234, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 80%, rgba(118, 75, 162, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 50%, rgba(102, 126, 234, 0.05) 0%, transparent 70%);
  pointer-events: none;
}

.airplane {
  position: absolute;
  font-size: 2.5rem;
  opacity: 0.08;
  animation: fly 25s linear infinite;
  filter: grayscale(100%);
}

@keyframes fly {
  0% {
    transform: translateX(-100px) translateY(0) rotate(45deg);
  }
  100% {
    transform: translateX(calc(100vw + 100px)) translateY(-30vh) rotate(45deg);
  }
}

.content {
  text-align: center;
  color: white;
  padding: 40px;
  max-width: 900px;
  z-index: 1;
}

h1 {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #ffffff 0%, #b0b0b0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 1.2rem;
  font-weight: 300;
  margin-bottom: 50px;
  color: #b0b0b0;
}

.stats {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 50px;
  flex-wrap: wrap;
}

.stat-box {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 25px 40px;
  min-width: 160px;
  transition: all 0.3s ease;
}

.stat-box:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(102, 126, 234, 0.3);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.15);
}

.stat-number {
  font-size: 2.8rem;
  font-weight: 700;
  display: block;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 0.85rem;
  color: #808080;
  text-transform: uppercase;
  letter-spacing: 1.5px;
}

.cta-button {
  display: inline-block;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 18px 50px;
  font-size: 1.1rem;
  font-weight: 600;
  text-decoration: none;
  border-radius: 50px;
  transition: all 0.3s ease;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
  border: none;
}

.cta-button:hover {
  transform: scale(1.05) translateY(-2px);
  box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
}

.features {
  margin-top: 60px;
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
}

.feature {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 12px 22px;
  border-radius: 25px;
  font-size: 0.9rem;
  color: #b0b0b0;
  transition: all 0.3s ease;
}

.feature:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(102, 126, 234, 0.3);
  color: white;
}

/* Fade in animation */
.fade-in {
  animation: fadeIn 0.8s ease-out forwards;
  opacity: 0;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  h1 {
    font-size: 2.5rem;
  }

  .subtitle {
    font-size: 1rem;
  }

  .stats {
    gap: 15px;
  }

  .stat-box {
    min-width: 130px;
    padding: 20px 25px;
  }

  .stat-number {
    font-size: 2.2rem;
  }

  .features {
    gap: 10px;
  }

  .feature {
    padding: 10px 18px;
    font-size: 0.85rem;
  }
}
</style>