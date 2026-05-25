// FPS ASMR Dessert Slicing Game - Core Engine

// --- AUDIO SYNTHESIZER (Web Audio API) ---
class ASMRSound {
    constructor() {
        this.ctx = null;
        this.masterVolume = null;
        this.muted = false;
        
        // Continuous slice audio nodes
        this.sliceNoise = null;
        this.sliceOsc = null;
        this.sliceFilter = null;
        this.sliceGain = null;
        this.sliceOscGain = null;
    }

    init() {
        if (this.ctx) return;
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        this.ctx = new AudioContext();
        this.masterVolume = this.ctx.createGain();
        this.masterVolume.gain.setValueAtTime(0.5, this.ctx.currentTime);
        this.masterVolume.connect(this.ctx.destination);
        console.log("Web Audio API initialized.");
    }

    setVolume(val) {
        if (!this.masterVolume) return;
        this.masterVolume.gain.setValueAtTime(val, this.ctx.currentTime);
    }

    toggleMute() {
        this.muted = !this.muted;
        if (this.masterVolume) {
            this.masterVolume.gain.setValueAtTime(this.muted ? 0 : 0.4, this.ctx.currentTime);
        }
        if (this.muted && 'speechSynthesis' in window) {
            window.speechSynthesis.cancel();
        }
        return this.muted;
    }

    // Synthesize a knock sound (glass knock)
    playKnock() {
        if (!this.ctx || this.muted) return;
        this.synthKnock(0);
        this.synthKnock(0.18);
    }

    synthKnock(delay) {
        const time = this.ctx.currentTime + delay;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        
        osc.type = 'sine';
        osc.frequency.setValueAtTime(140, time);
        osc.frequency.exponentialRampToValueAtTime(70, time + 0.08);
        
        gain.gain.setValueAtTime(0, time);
        gain.gain.linearRampToValueAtTime(0.8, time + 0.005);
        gain.gain.exponentialRampToValueAtTime(0.01, time + 0.12);
        
        osc.connect(gain);
        gain.connect(this.masterVolume);
        
        osc.start(time);
        osc.stop(time + 0.15);
    }

    // Synthesize satisfying slice sound (wet sponge slice end)
    playSlice() {
        if (!this.ctx || this.muted) return;
        
        const time = this.ctx.currentTime;
        const bufferSize = this.ctx.sampleRate * 0.3; // 300ms
        const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const data = buffer.getChannelData(0);
        
        for (let i = 0; i < bufferSize; i++) {
            data[i] = Math.random() * 2 - 1;
        }
        
        const noise = this.ctx.createBufferSource();
        noise.buffer = buffer;
        
        const filter = this.ctx.createBiquadFilter();
        filter.type = 'bandpass';
        filter.Q.setValueAtTime(3.0, time);
        filter.frequency.setValueAtTime(1000, time);
        filter.frequency.exponentialRampToValueAtTime(350, time + 0.25);
        
        const gain = this.ctx.createGain();
        gain.gain.setValueAtTime(0, time);
        gain.gain.linearRampToValueAtTime(0.2, time + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.001, time + 0.3);
        
        const lowOsc = this.ctx.createOscillator();
        const lowGain = this.ctx.createGain();
        lowOsc.type = 'triangle';
        lowOsc.frequency.setValueAtTime(70, time);
        lowOsc.frequency.linearRampToValueAtTime(40, time + 0.2);
        
        lowGain.gain.setValueAtTime(0.12, time);
        lowGain.gain.exponentialRampToValueAtTime(0.001, time + 0.25);
        
        noise.connect(filter);
        filter.connect(gain);
        gain.connect(this.masterVolume);
        
        lowOsc.connect(lowGain);
        lowGain.connect(this.masterVolume);
        
        noise.start(time);
        noise.stop(time + 0.3);
        lowOsc.start(time);
        lowOsc.stop(time + 0.3);
    }

    // Continuous Slicing Sound ASMR loop
    startContinuousSlice() {
        if (!this.ctx || this.muted) return;
        
        const time = this.ctx.currentTime;
        
        // Setup looping noise buffer
        const bufferSize = this.ctx.sampleRate * 2.0;
        const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
            data[i] = Math.random() * 2 - 1;
        }
        
        this.sliceNoise = this.ctx.createBufferSource();
        this.sliceNoise.buffer = buffer;
        this.sliceNoise.loop = true;
        
        this.sliceFilter = this.ctx.createBiquadFilter();
        this.sliceFilter.type = 'bandpass';
        this.sliceFilter.Q.setValueAtTime(4.0, time);
        this.sliceFilter.frequency.setValueAtTime(350, time);
        
        this.sliceGain = this.ctx.createGain();
        this.sliceGain.gain.setValueAtTime(0.001, time);
        
        this.sliceOsc = this.ctx.createOscillator();
        this.sliceOsc.type = 'triangle';
        this.sliceOsc.frequency.setValueAtTime(40, time);
        this.sliceOscGain = this.ctx.createGain();
        this.sliceOscGain.gain.setValueAtTime(0.001, time);
        
        this.sliceNoise.connect(this.sliceFilter);
        this.sliceFilter.connect(this.sliceGain);
        this.sliceGain.connect(this.masterVolume);
        
        this.sliceOsc.connect(this.sliceOscGain);
        this.sliceOscGain.connect(this.masterVolume);
        
        this.sliceNoise.start(time);
        this.sliceOsc.start(time);
    }

    // Synthesize micro crackles / pops for ASMR textures
    playCrackle(isCrispy = false) {
        if (!this.ctx || this.muted) return;
        
        const time = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        
        osc.type = isCrispy ? 'triangle' : 'sine';
        osc.frequency.setValueAtTime(isCrispy ? 3500 : 2500, time);
        osc.frequency.exponentialRampToValueAtTime(isCrispy ? 800 : 1500, time + 0.008);
        
        gain.gain.setValueAtTime(0.001, time);
        gain.gain.linearRampToValueAtTime(isCrispy ? 0.08 : 0.03, time + 0.001);
        gain.gain.exponentialRampToValueAtTime(0.001, time + 0.008);
        
        osc.connect(gain);
        gain.connect(this.masterVolume);
        
        osc.start(time);
        osc.stop(time + 0.01);
    }

    // Dynamic updates based on mouse speed (pixels/frame)
    updateContinuousSlice(speed) {
        if (!this.ctx || this.muted || !this.sliceGain) return;
        
        const time = this.ctx.currentTime;
        let normSpeed = Math.min(speed / 30.0, 1.0); // Normalize up to 30px per frame drag
        
        if (normSpeed < 0.05) {
            // Mouse is still, mute scraping
            this.sliceGain.gain.setTargetAtTime(0.002, time, 0.05);
            this.sliceOscGain.gain.setTargetAtTime(0.002, time, 0.05);
        } else {
            let targetGain = normSpeed * 0.22;
            let targetFreq = 250 + normSpeed * 650; // Sweeps from 250Hz up to 900Hz
            let targetOscGain = normSpeed * 0.15;
            
            this.sliceGain.gain.setTargetAtTime(targetGain, time, 0.02);
            this.sliceFilter.frequency.setTargetAtTime(targetFreq, time, 0.02);
            
            this.sliceOscGain.gain.setTargetAtTime(targetOscGain, time, 0.02);
            this.sliceOsc.frequency.setTargetAtTime(35 + normSpeed * 45, time, 0.02);
            
            // Trigger rapid ASMR crackling sounds depending on dessert level
            if (gameState.currentLevel === 2 && Math.random() < 0.18) {
                // Revani: sticky syrup pops
                this.playCrackle(false);
            } else if (gameState.currentLevel === 3 && Math.random() < 0.45) {
                // Baklava: crispy flaky pastry snaps
                this.playCrackle(true);
            }
        }
    }

    stopContinuousSlice() {
        const time = this.ctx.currentTime;
        
        if (this.sliceGain) {
            this.sliceGain.gain.setValueAtTime(this.sliceGain.gain.value, time);
            this.sliceGain.gain.exponentialRampToValueAtTime(0.001, time + 0.1);
        }
        if (this.sliceOscGain) {
            this.sliceOscGain.gain.setValueAtTime(this.sliceOscGain.gain.value, time);
            this.sliceOscGain.gain.exponentialRampToValueAtTime(0.001, time + 0.1);
        }
        
        setTimeout(() => {
            try {
                if (this.sliceNoise) { this.sliceNoise.stop(); this.sliceNoise.disconnect(); }
                if (this.sliceOsc) { this.sliceOsc.stop(); this.sliceOsc.disconnect(); }
            } catch(e) {}
            this.sliceNoise = null;
            this.sliceOsc = null;
            this.sliceFilter = null;
            this.sliceGain = null;
            this.sliceOscGain = null;
        }, 120);
    }

    // Synthesize spatula scraping metal and cake scooping
    playScoop() {
        if (!this.ctx || this.muted) return;
        
        const time = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(300, time);
        osc.frequency.linearRampToValueAtTime(480, time + 0.2);
        osc.frequency.linearRampToValueAtTime(200, time + 0.4);
        
        gain.gain.setValueAtTime(0, time);
        gain.gain.linearRampToValueAtTime(0.1, time + 0.05);
        gain.gain.exponentialRampToValueAtTime(0.001, time + 0.45);
        
        const bufferSize = this.ctx.sampleRate * 0.4;
        const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
            data[i] = Math.random() * 2 - 1;
        }
        
        const noise = this.ctx.createBufferSource();
        noise.buffer = buffer;
        
        const filter = this.ctx.createBiquadFilter();
        filter.type = 'highpass';
        filter.frequency.setValueAtTime(2500, time);
        
        const noiseGain = this.ctx.createGain();
        noiseGain.gain.setValueAtTime(0, time);
        noiseGain.gain.linearRampToValueAtTime(0.03, time + 0.1);
        noiseGain.gain.exponentialRampToValueAtTime(0.001, time + 0.4);
        
        osc.connect(gain);
        gain.connect(this.masterVolume);
        
        noise.connect(filter);
        filter.connect(noiseGain);
        noiseGain.connect(this.masterVolume);
        
        osc.start(time);
        osc.stop(time + 0.45);
        
        noise.start(time);
        noise.stop(time + 0.45);
    }

    // Success bell chime
    playSuccess() {
        if (!this.ctx || this.muted) return;
        
        const now = this.ctx.currentTime;
        const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
        
        notes.forEach((freq, idx) => {
            const time = now + idx * 0.08;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            
            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, time);
            
            gain.gain.setValueAtTime(0, time);
            gain.gain.linearRampToValueAtTime(0.2, time + 0.02);
            gain.gain.exponentialRampToValueAtTime(0.001, time + 0.4);
            
            osc.connect(gain);
            gain.connect(this.masterVolume);
            
            osc.start(time);
            osc.stop(time + 0.5);
        });
    }

    // Unhappy customer groan / synth buzz
    playFail() {
        if (!this.ctx || this.muted) return;
        
        const time = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(150, time);
        osc.frequency.linearRampToValueAtTime(90, time + 0.4);
        
        const filter = this.ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(300, time);
        
        gain.gain.setValueAtTime(0, time);
        gain.gain.linearRampToValueAtTime(0.25, time + 0.05);
        gain.gain.exponentialRampToValueAtTime(0.001, time + 0.45);
        
        osc.connect(filter);
        filter.connect(gain);
        gain.connect(this.masterVolume);
        
        osc.start(time);
        osc.stop(time + 0.45);
    }

    // Speak customer dialogue text out loud using Web Speech Synthesis (Dış Ses / Voiceover)
    speakDialogue(text, lang = 'tr-TR') {
        if (this.muted || !('speechSynthesis' in window)) return;
        
        // Strip HTML tags
        const cleanText = text.replace(/<[^>]*>/g, '');
        
        // Cancel existing speech
        window.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = lang;
        
        // Find best voice
        const voices = window.speechSynthesis.getVoices();
        const langVoices = voices.filter(v => v.lang.startsWith(lang.split('-')[0]));
        
        if (gameState.customerData) {
            const name = gameState.customerData.name;
            if (name === "Emre") {
                utterance.pitch = 1.0; // Friendly young male tone
                utterance.rate = 0.96;
                const male = langVoices.find(v => v.name.toLowerCase().includes('male') || v.name.toLowerCase().includes('tolga'));
                if (male) utterance.voice = male;
            } else if (name === "Kerem") {
                utterance.pitch = 0.9; // Gamer / developer male tone
                utterance.rate = 0.98;
                const male = langVoices.find(v => v.name.toLowerCase().includes('male') || v.name.toLowerCase().includes('tolga'));
                if (male) utterance.voice = male;
            } else if (name === "Yeni Evliler") {
                utterance.pitch = 1.15; // Excited female voice (Bride speaking)
                utterance.rate = 1.02;
                const female = langVoices.find(v => v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('yelda') || v.name.toLowerCase().includes('google'));
                if (female) utterance.voice = female;
            }
        }
        
        // Lower other game sounds slightly while speaking
        this.setVolume(0.15);
        utterance.onend = () => {
            this.setVolume(0.4);
        };
        utterance.onerror = () => {
            this.setVolume(0.4);
        };
        
        window.speechSynthesis.speak(utterance);
    }
}

const audio = new ASMRSound();

// --- GEOMETRY FUNCTIONS ---

// Compute distance between 2 points
function dist(p1, p2) {
    return Math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2);
}

// Line intersection solver: Segment 1 (p1 -> p2) and Segment 2 (p3 -> p4)
function getLineIntersection(p1, p2, p3, p4) {
    let denominator = (p4.y - p3.y) * (p2.x - p1.x) - (p4.x - p3.x) * (p2.y - p1.y);
    if (denominator === 0) return null; // Parallel lines
    
    let ua = ((p4.x - p3.x) * (p1.y - p3.y) - (p4.y - p3.y) * (p1.x - p3.x)) / denominator;
    let ub = ((p2.x - p1.x) * (p1.y - p3.y) - (p2.y - p1.y) * (p1.x - p3.x)) / denominator;
    
    const eps = 0.0001;
    if (ua >= -eps && ua <= 1 + eps && ub >= -eps && ub <= 1 + eps) {
        return {
            x: p1.x + ua * (p2.x - p1.x),
            y: p1.y + ua * (p2.y - p1.y)
        };
    }
    return null;
}

// Check if point is inside polygon
function isPointInPolygon(p, poly) {
    let inside = false;
    for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
        let xi = poly[i].x, yi = poly[i].y;
        let xj = poly[j].x, yj = poly[j].y;
        
        let intersect = ((yi > p.y) !== (yj > p.y))
            && (p.x < (xj - xi) * (p.y - yi) / (yj - yi) + xi);
        if (intersect) inside = !inside;
    }
    return inside;
}

// Calculate polygon centroid
function getPolygonCentroid(poly) {
    let x = 0, y = 0, area = 0;
    let n = poly.length;
    for (let i = 0; i < n; i++) {
        let p1 = poly[i];
        let p2 = poly[(i + 1) % n];
        let factor = (p1.x * p2.y - p2.x * p1.y);
        x += (p1.x + p2.x) * factor;
        y += (p1.y + p2.y) * factor;
        area += factor;
    }
    area = area / 2;
    if (area === 0) return poly[0];
    return {
        x: x / (6 * area),
        y: y / (6 * area)
    };
}

// Calculate polygon area
function getPolygonArea(poly) {
    let area = 0;
    let n = poly.length;
    for (let i = 0; i < n; i++) {
        let p1 = poly[i];
        let p2 = poly[(i + 1) % n];
        area += (p1.x * p2.y - p2.x * p1.y);
    }
    return Math.abs(area / 2);
}

// Split polygon with a line segment
function splitPolygon(poly, p1, p2) {
    let intersections = [];
    let n = poly.length;
    
    for (let i = 0; i < n; i++) {
        let a = poly[i];
        let b = poly[(i + 1) % n];
        let intersect = getLineIntersection(p1, p2, a, b);
        if (intersect) {
            // Avoid adding duplicate points on vertices
            if (intersections.every(item => dist(item.point, intersect) > 1.5)) {
                intersections.push({
                    point: intersect,
                    edgeIndex: i
                });
            }
        }
    }
    
    // Can only split if it cuts exactly across two distinct edges
    if (intersections.length !== 2) {
        return null;
    }
    
    // Sort intersections by edge index to slice loops properly
    intersections.sort((a, b) => a.edgeIndex - b.edgeIndex);
    
    let int1 = intersections[0];
    let int2 = intersections[1];
    
    // Poly 1 vertices
    let poly1 = [int1.point];
    for (let i = int1.edgeIndex + 1; i <= int2.edgeIndex; i++) {
        poly1.push(poly[i]);
    }
    poly1.push(int2.point);
    
    // Poly 2 vertices
    let poly2 = [int2.point];
    for (let i = (int2.edgeIndex + 1) % n; ; i = (i + 1) % n) {
        poly2.push(poly[i]);
        if (i === int1.edgeIndex) break;
    }
    poly2.push(int1.point);
    
    return [poly1, poly2];
}

// Project a finite swipe line all the way to tray boundaries
function projectLineToTrayBounds(p1, p2, width, height) {
    let dx = p2.x - p1.x;
    let dy = p2.y - p1.y;
    let length = Math.sqrt(dx*dx + dy*dy);
    if (length < 2) return null; // Too short to cut
    
    let ux = dx / length;
    let uy = dy / length;
    
    // Line equation: P(t) = p1 + t * u
    let intersections = [];
    
    // Intersect with boundary x = 0
    if (ux !== 0) {
        let t = -p1.x / ux;
        let y = p1.y + t * uy;
        if (y >= 0 && y <= height) intersections.push({x: 0, y: y});
    }
    // Intersect with boundary x = width
    if (ux !== 0) {
        let t = (width - p1.x) / ux;
        let y = p1.y + t * uy;
        if (y >= 0 && y <= height) intersections.push({x: width, y: y});
    }
    // Intersect with boundary y = 0
    if (uy !== 0) {
        let t = -p1.y / uy;
        let x = p1.x + t * ux;
        if (x >= 0 && x <= width) intersections.push({x: x, y: 0});
    }
    // Intersect with boundary y = height
    if (uy !== 0) {
        let t = (height - p1.y) / uy;
        let x = p1.x + t * ux;
        if (x >= 0 && x <= width) intersections.push({x: x, y: height});
    }
    
    // Deduplicate
    let unique = [];
    intersections.forEach(pt => {
        if (unique.every(u => dist(u, pt) > 0.1)) {
            unique.push(pt);
        }
    });
    
    if (unique.length >= 2) {
        return {p1: unique[0], p2: unique[1]};
    }
    return null;
}

// Generate circular 32-sided polygon
function generateCirclePolygon(cx, cy, r, segments = 32) {
    let poly = [];
    for (let i = 0; i < segments; i++) {
        let angle = (i / segments) * Math.PI * 2;
        poly.push({
            x: cx + Math.cos(angle) * r,
            y: cy + Math.sin(angle) * r
        });
    }
    return poly;
}


// --- GAME VARIABLES & STATE ---

const W = 560; // Dessert tray width
const H = 320; // Dessert tray height

let gameState = {
    currentLevel: 1, // 1: Trileçe, 2: Revani, 3: Baklava
    currentDay: 1,
    cash: 0.0,
    tipsEarned: 0.0,
    expenses: 0.0,
    customersServed: 0,
    averageAccuracy: 0.0,
    
    // Tools: 'knife', 'spatula'
    activeTool: 'knife',
    
    // Current Tray data
    trayPolygons: [], // Array of polygons {id, vertices: [{x,y}...]}
    polygonIdCounter: 0,
    servedSliceId: null, // ID of polygon currently picked up by spatula
    isScooped: false,
    
    // Slicing/Drag state on tray
    isDrawingCut: false,
    cutStart: {x: 0, y: 0},
    cutCurrent: {x: 0, y: 0},
    lastMousePos: {x: 0, y: 0},
    cutLines: [], // visual lines drawn so far
    trayParticles: [], // flying particles for ASMR visual feedback
    showCorrectCutGuide: false, // show outline of correct cut shape on failure
    
    // Customer Queue State
    customerIndex: 0,
    customerMax: 3, // 3 customers per day
    customerData: null, // Current active customer details
    customerState: 'idle', // 'idle', 'entering', 'talking', 'drawing', 'waiting', 'serving', 'evaluating', 'leaving'
    
    // Scoring & Target
    targetPolygon: null, // The ideal slice the customer wanted
    dayAccuracySum: 0,
    dayAccuracyCount: 0
};

// Customer definitions database
const CUSTOMER_PROFILES = [
    {
        name: "Emre",
        avatar: `<svg viewBox="0 0 100 120" class="customer-svg">
            <!-- Neck & Body -->
            <rect x="30" y="80" width="40" height="40" fill="#f5ebd6" rx="4" />
            <!-- Skin Neck -->
            <path d="M42 75 L58 75 L55 85 L45 85 Z" fill="#eed1b7" />
            <!-- V-neck collar of open beige shirt -->
            <path d="M42 80 L50 92 L58 80" stroke="#eed1b7" stroke-width="4" fill="none" />
            <path d="M30 80 L42 95 L50 92 L58 95 L70 80" stroke="#e1cca9" stroke-width="2.5" fill="none" />
            
            <!-- Head -->
            <circle cx="50" cy="50" r="26" fill="#eed1b7" />
            
            <!-- Short black hair -->
            <path d="M24 45 C 24 22, 76 22, 76 45 C 72 40, 68 38, 50 38 C 32 38, 28 40, 24 45 Z" fill="#1c1c1c" />
            <path d="M24 45 L27 58 L24 60 Z M76 45 L73 58 L76 60 Z" fill="#1c1c1c" />
            
            <!-- Beard & Mustache -->
            <path d="M26 55 C 28 75, 72 75, 74 55 C 68 62, 50 68, 50 68 C 50 68, 32 62, 26 55 Z" fill="#2d2d2d" />
            <!-- Mustache details -->
            <path d="M36 64 C 44 60, 50 65, 50 65 C 50 65, 56 60, 64 64 C 55 70, 45 70, 36 64 Z" fill="#1c1c1c" />
            
            <!-- Eyes -->
            <circle cx="41" cy="48" r="3.5" fill="#2d2d2d" />
            <circle cx="59" cy="48" r="3.5" fill="#2d2d2d" />
            <!-- Eyebrows -->
            <rect x="35" y="42" width="11" height="3" fill="#1c1c1c" rx="1" transform="rotate(-3 40 42)"/>
            <rect x="54" y="42" width="11" height="3" fill="#1c1c1c" rx="1" transform="rotate(3 60 42)"/>
            <!-- Nose -->
            <path d="M47 48 Q 50 55 53 48" stroke="#d5bfa7" stroke-width="2.5" fill="none" stroke-linecap="round"/>
            
            <!-- Animated Arms -->
            <g class="customer-left-arm" style="transform-origin: 30px 92px;">
                <path d="M30 92 C 18 98, 12 108, 20 120" stroke="#f5ebd6" stroke-width="12" stroke-linecap="round" fill="none" />
                <circle cx="20" cy="120" r="7" fill="#eed1b7" />
            </g>
            <g class="customer-right-arm" style="transform-origin: 70px 92px;">
                <path d="M70 92 C 82 98, 88 108, 80 120" stroke="#f5ebd6" stroke-width="12" stroke-linecap="round" fill="none" />
                <circle cx="80" cy="120" r="7" fill="#eed1b7" />
            </g>
        </svg>`,
        dialogues: {
            1: "Selamlar usta! Şöyle tam dikey ortadan güzel bir dilim kesebilir misin? Yarısını bana ver gerisi tezgaha.",
            2: "Usta kolay gelsin, tatlıların nefis görünüyor. Bana çaprazından büyük bir dilim keser misin?",
            3: "Hayırlı işler! Baklavanın çıtırlığı harika. Şöyle 8 dilim yapıp birini bana verir misin?"
        },
        setupTarget: (level) => {
            if (level === 1) {
                // Vertical half slice (Left half)
                gameState.targetPolygon = [
                    {x: 0, y: 0}, {x: W/2, y: 0}, {x: W/2, y: H}, {x: 0, y: H}
                ];
                return [{p1: {x: W/2, y: 0}, p2: {x: W/2, y: H}}];
            } else if (level === 2) {
                // Diagonal slice (bottom-left half)
                gameState.targetPolygon = [
                    {x: 0, y: 0}, {x: W, y: H}, {x: 0, y: H}
                ];
                return [{p1: {x: 0, y: 0}, p2: {x: W, y: H}}];
            } else {
                // Radial cut (one 1/8 wedge from a circle of radius 140)
                const cx = W/2, cy = H/2, r = 140;
                let poly = [{x: cx, y: cy}];
                poly.push({x: cx + r, y: cy});
                poly.push({x: cx + Math.cos(Math.PI/4) * r, y: cy + Math.sin(Math.PI/4) * r});
                gameState.targetPolygon = poly;
                
                return [
                    {p1: {x: cx - r, y: cy}, p2: {x: cx + r, y: cy}},
                    {p1: {x: cx, y: cy - r}, p2: {x: cx, y: cy + r}},
                    {p1: {x: cx - r * Math.cos(Math.PI/4), y: cy - r * Math.sin(Math.PI/4)}, p2: {x: cx + r * Math.cos(Math.PI/4), y: cy + r * Math.sin(Math.PI/4)}},
                    {p1: {x: cx - r * Math.cos(Math.PI/4), y: cy + r * Math.sin(Math.PI/4)}, p2: {x: cx + r * Math.cos(Math.PI/4), y: cy - r * Math.sin(Math.PI/4)}}
                ];
            }
        }
    },
    {
        name: "Kerem",
        avatar: `<svg viewBox="0 0 100 120" class="customer-svg">
            <!-- Blue Hoodie Neck/Body -->
            <rect x="30" y="80" width="40" height="40" fill="#3a6fb3" rx="6" />
            <path d="M30 80 Q 50 92 70 80" stroke="#2c558c" stroke-width="4.5" fill="none" />
            
            <!-- Skin Neck -->
            <rect x="44" y="72" width="12" height="12" fill="#fcd1a1" />
            
            <!-- Head -->
            <circle cx="50" cy="48" r="25" fill="#fcd1a1" />
            
            <!-- Wavy/Curly Black Hair -->
            <path d="M23 42 C 22 18, 78 18, 77 42 C 72 35, 68 32, 50 32 C 32 32, 28 35, 23 42 Z" fill="#1f1f1f" />
            <circle cx="30" cy="30" r="6" fill="#1f1f1f" />
            <circle cx="40" cy="25" r="7" fill="#1f1f1f" />
            <circle cx="50" cy="24" r="7" fill="#1f1f1f" />
            <circle cx="60" cy="26" r="6" fill="#1f1f1f" />
            <circle cx="70" cy="31" r="6" fill="#1f1f1f" />
            
            <!-- Black Rectangular Glasses -->
            <rect x="31" y="40" width="16" height="11" rx="2.5" fill="none" stroke="#111" stroke-width="2.5" />
            <rect x="53" y="40" width="16" height="11" rx="2.5" fill="none" stroke="#111" stroke-width="2.5" />
            <line x1="47" y1="45" x2="53" y2="45" stroke="#111" stroke-width="2.5" />
            
            <!-- Beard & Mustache -->
            <path d="M26 53 C 28 72, 72 72, 74 53 C 68 60, 50 65, 50 65 C 50 65, 32 60, 26 53 Z" fill="#333" />
            <path d="M37 60 Q 50 63 63 60" stroke="#1a1a1a" stroke-width="2" fill="none" />
            
            <!-- Eyes behind glasses -->
            <circle cx="39" cy="45" r="2.5" fill="#111" />
            <circle cx="61" cy="45" r="2.5" fill="#111" />
            
            <!-- Nose & Mouth -->
            <path d="M47 45 Q 50 51 53 45" stroke="#e59f6d" stroke-width="2" fill="none" />
            <path d="M44 64 Q 50 68 56 64" stroke="#d59f6d" stroke-width="2" fill="none" />
            
            <!-- Animated Arms -->
            <g class="customer-left-arm" style="transform-origin: 30px 92px;">
                <path d="M30 92 C 20 98, 14 108, 22 120" stroke="#3a6fb3" stroke-width="12" stroke-linecap="round" fill="none" />
                <circle cx="22" cy="120" r="7" fill="#fcd1a1" />
            </g>
            <g class="customer-right-arm" style="transform-origin: 70px 92px;">
                <path d="M70 92 C 80 98, 86 108, 78 120" stroke="#3a6fb3" stroke-width="12" stroke-linecap="round" fill="none" />
                <circle cx="78" cy="120" r="7" fill="#fcd1a1" />
            </g>
        </svg>`,
        dialogues: {
            1: "Usta selamlar! Yazılım kodlarken canım çok tatlı çekti. Şuradan küçük bir kare dilim alabilir miyim?",
            2: "Selam usta! Revaniyi çok severim. Bana şöyle şık bir eşkenar dilim kesiver hele.",
            3: "Kolay gelsin usta! Şerbetli fıstıklı baklavanın göbeğinden bana küçük bir dilim verir misin?"
        },
        setupTarget: (level) => {
            if (level === 1) {
                // Small corner square (Top-Right, 100x100)
                gameState.targetPolygon = [
                    {x: W - 100, y: 0}, {x: W, y: 0}, {x: W, y: 100}, {x: W - 100, y: 100}
                ];
                return [
                    {p1: {x: W - 100, y: 0}, p2: {x: W - 100, y: H}},
                    {p1: {x: 0, y: 100}, p2: {x: W, y: 100}}
                ];
            } else if (level === 2) {
                // Small diamond at corner
                gameState.targetPolygon = [
                    {x: W - 80, y: 0}, {x: W, y: 0}, {x: W, y: 60}, {x: W - 80, y: 60}
                ];
                return [
                    {p1: {x: W - 80, y: 0}, p2: {x: W - 80, y: H}},
                    {p1: {x: 0, y: 60}, p2: {x: W, y: 60}}
                ];
            } else {
                // Small wedge at edge
                const cx = W/2, cy = H/2, r = 140;
                let poly = [{x: cx, y: cy}];
                poly.push({x: cx + r * Math.cos(-Math.PI/12), y: cy + r * Math.sin(-Math.PI/12)});
                poly.push({x: cx + r * Math.cos(Math.PI/12), y: cy + r * Math.sin(Math.PI/12)});
                gameState.targetPolygon = poly;
                
                return [
                    {p1: {x: cx, y: cy}, p2: {x: cx + r * Math.cos(-Math.PI/12), y: cy + r * Math.sin(-Math.PI/12)}},
                    {p1: {x: cx, y: cy}, p2: {x: cx + r * Math.cos(Math.PI/12), y: cy + r * Math.sin(Math.PI/12)}}
                ];
            }
        }
    },
    {
        name: "Yeni Evliler",
        avatar: `<svg viewBox="0 0 100 120" class="customer-svg">
            <!-- Bride & Groom side by side -->
            <!-- Groom Body (Right) -->
            <rect x="53" y="80" width="28" height="40" fill="#1a1a1a" rx="4" />
            <path d="M61 80 L67 94 L73 80 Z" fill="#ffffff" />
            <path d="M65 85 L69 85 L68 98 L66 98 Z" fill="#111" />
            <rect x="63" y="72" width="8" height="10" fill="#eed1b7" />
            <circle cx="67" cy="54" r="18" fill="#eed1b7" />
            <path d="M49 50 C 49 35, 83 35, 83 50 Z" fill="#1c1c1c" />
            <path d="M50 56 C 52 68, 80 68, 82 56 Z" fill="#2d2d2d" opacity="0.7" />
            <circle cx="60" cy="51" r="2" fill="#111" />
            <circle cx="72" cy="51" r="2" fill="#111" />
            <path d="M61 61 Q 67 67 72 61" stroke="#e84a5f" stroke-width="1.8" fill="none" />
            
            <!-- Bride Body (Left) -->
            <path d="M18 80 L47 80 L43 120 L21 120 Z" fill="#ffffff" />
            <rect x="28" y="72" width="8" height="10" fill="#fcd1a1" />
            <circle cx="32" cy="52" r="18" fill="#fcd1a1" />
            <!-- Back Hair -->
            <path d="M12 52 C 12 32, 52 32, 52 52 C 52 72, 46 82, 46 95 H18 Z" fill="#5c4033" />
            <!-- Tiara -->
            <path d="M22 36 L26 31 L32 26 L38 31 L42 36 Z" fill="#d4af37" stroke="#fff" stroke-width="0.8" />
            <!-- Veil -->
            <path d="M12 36 Q 32 20 52 36 Q 57 65 53 105 H12 Z" fill="rgba(255,255,255,0.35)" />
            <circle cx="26" cy="51" r="2" fill="#111" />
            <circle cx="38" cy="51" r="2" fill="#111" />
            <path d="M27 61 Q 32 66 37 61" stroke="#e84a5f" stroke-width="1.8" fill="none" />
            
            <!-- Animated Arms -->
            <!-- Bride's Left Arm (White Lace) -->
            <g class="customer-left-arm" style="transform-origin: 20px 82px;">
                <path d="M20 82 C 10 88, 4 98, 12 110" stroke="#ffffff" stroke-width="10" stroke-linecap="round" fill="none" />
                <circle cx="12" cy="110" r="6" fill="#fcd1a1" />
            </g>
            <!-- Groom's Right Arm (Black Tuxedo) -->
            <g class="customer-right-arm" style="transform-origin: 80px 82px;">
                <path d="M80 82 C 90 88, 96 98, 88 110" stroke="#1a1a1a" stroke-width="12" stroke-linecap="round" fill="none" />
                <circle cx="88" cy="110" r="6" fill="#eed1b7" />
            </g>
        </svg>`,
        dialogues: {
            1: "Selamlar usta! Düğünümüzden çıktık, ağzımız tatlansın diye geldik! Bize şöyle büyük bir yarım dilim kesebilir misin?",
            2: "Usta hayırlı işler! En mutlu günümüzde bize şık bir baklava/eşkenar dilim kesip verir misin?",
            3: "Selamlar usta! Düğün bitti, şimdi tatlı zamanı! Bize baklavanın tam ortasındaki o nefis yuvarlak göbeği çıkarır mısın?"
        },
        setupTarget: (level) => {
            if (level === 1) {
                // Center triangle from cross cut
                gameState.targetPolygon = [
                    {x: 0, y: 0}, {x: W, y: 0}, {x: W/2, y: H/2}
                ];
                return [
                    {p1: {x: 0, y: 0}, p2: {x: W, y: H}},
                    {p1: {x: W, y: 0}, p2: {x: 0, y: H}}
                ];
            } else if (level === 2) {
                // One of the diagonal diamond cuts in the middle
                gameState.targetPolygon = [
                    {x: W/2 - 60, y: H/2}, {x: W/2, y: H/2 - 40}, {x: W/2 + 60, y: H/2}, {x: W/2, y: H/2 + 40}
                ];
                return [
                    {p1: {x: 0, y: 40}, p2: {x: W - 120, y: H}},
                    {p1: {x: 120, y: 0}, p2: {x: W, y: H - 40}},
                    {p1: {x: W, y: 40}, p2: {x: 120, y: H}},
                    {p1: {x: W - 120, y: 0}, p2: {x: 0, y: H - 40}}
                ];
            } else {
                // Inner concentric circle core
                const cx = W/2, cy = H/2, r = 60;
                gameState.targetPolygon = generateCirclePolygon(cx, cy, r, 20);
                
                let cuts = [];
                for (let i = 0; i < 16; i++) {
                    let a1 = (i / 16) * Math.PI * 2;
                    let a2 = ((i + 1) / 16) * Math.PI * 2;
                    cuts.push({
                        p1: {x: cx + Math.cos(a1) * r, y: cy + Math.sin(a1) * r},
                        p2: {x: cx + Math.cos(a2) * r, y: cy + Math.sin(a2) * r}
                    });
                }
                return cuts;
            }
        }
    }
];

// --- CANVAS RENDERERS ---

const glassCanvas = document.getElementById("glass-window");
const glassCtx = glassCanvas.getContext("2d");
const dessertCanvas = document.getElementById("dessert-canvas");
const dessertCtx = dessertCanvas.getContext("2d");

// Resize glass canvas based on container dimensions
function resizeGlassCanvas() {
    const rect = glassCanvas.getBoundingClientRect();
    glassCanvas.width = rect.width;
    glassCanvas.height = rect.height;
    drawFog();
}

// Draw foggy window layer
let fogOpacity = 0.85;
function drawFog() {
    glassCtx.clearRect(0, 0, glassCanvas.width, glassCanvas.height);
    
    // Create soft frosty white glass gradient
    glassCtx.fillStyle = `rgba(225, 235, 255, ${fogOpacity})`;
    glassCtx.fillRect(0, 0, glassCanvas.width, glassCanvas.height);
    
    // Draw neon border of window frame
    glassCtx.strokeStyle = 'rgba(255, 155, 38, 0.4)';
    glassCtx.lineWidth = 8;
    glassCtx.strokeRect(0, 0, glassCanvas.width, glassCanvas.height);
}

// Clean specific trace on foggy glass (scratching/drawing effect)
function clearFogTrace(x, y, radius = 24) {
    glassCtx.save();
    glassCtx.globalCompositeOperation = 'destination-out';
    
    // Draw blurry brush
    let grad = glassCtx.createRadialGradient(x, y, 0, x, y, radius);
    grad.addColorStop(0, 'rgba(0, 0, 0, 1)');
    grad.addColorStop(0.5, 'rgba(0, 0, 0, 0.6)');
    grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
    
    glassCtx.fillStyle = grad;
    glassCtx.beginPath();
    glassCtx.arc(x, y, radius, 0, Math.PI * 2);
    glassCtx.fill();
    
    glassCtx.restore();
}

// Draw dessert tray graphics
function drawDessertTray() {
    dessertCtx.clearRect(0, 0, W, H);
    
    // 1. Draw metal tray bottom (revealed when pieces are scooped)
    dessertCtx.fillStyle = '#4a4753';
    dessertCtx.fillRect(0, 0, W, H);
    // Brushed metal details
    dessertCtx.strokeStyle = '#383640';
    dessertCtx.lineWidth = 1;
    for (let i = 10; i < W; i += 20) {
        dessertCtx.beginPath();
        dessertCtx.moveTo(i, 0);
        dessertCtx.lineTo(i, H);
        dessertCtx.stroke();
    }
    
    // If level is Baklava (circular tray), draw metallic circular background first
    if (gameState.currentLevel === 3) {
        dessertCtx.save();
        dessertCtx.beginPath();
        dessertCtx.arc(W/2, H/2, 145, 0, Math.PI*2);
        dessertCtx.fillStyle = '#222';
        dessertCtx.fill();
        dessertCtx.strokeStyle = '#555';
        dessertCtx.lineWidth = 5;
        dessertCtx.stroke();
        dessertCtx.restore();
    }
    
    // 2. Render each remaining dessert slice polygon
    gameState.trayPolygons.forEach(poly => {
        if (poly.id === gameState.servedSliceId) return; // Skip currently scooped slice
        
        dessertCtx.save();
        
        // Define path
        dessertCtx.beginPath();
        dessertCtx.moveTo(poly.vertices[0].x, poly.vertices[0].y);
        for (let i = 1; i < poly.vertices.length; i++) {
            dessertCtx.lineTo(poly.vertices[i].x, poly.vertices[i].y);
        }
        dessertCtx.closePath();
        
        // Clip to drawing area
        dessertCtx.clip();
        
        // Fill dessert texture base
        if (gameState.currentLevel === 1) { // Trileçe
            // Milk soaked sponge base
            dessertCtx.fillStyle = '#fff6de';
            dessertCtx.fillRect(0, 0, W, H);
            
            // Caramel Glaze Top Layer
            let grad = dessertCtx.createLinearGradient(0, 0, W, H);
            grad.addColorStop(0, '#c3752e');
            grad.addColorStop(0.5, '#b05e19');
            grad.addColorStop(1, '#944b0f');
            dessertCtx.fillStyle = grad;
            dessertCtx.fillRect(0, 0, W, H);
            
            // Traditional white cream swirls on top
            dessertCtx.strokeStyle = 'rgba(255,255,255,0.7)';
            dessertCtx.lineWidth = 3.5;
            dessertCtx.beginPath();
            for (let x = -50; x < W + 50; x += 30) {
                dessertCtx.moveTo(x, -50);
                dessertCtx.bezierCurveTo(x + 15, H/2, x - 15, H/2, x, H + 50);
            }
            dessertCtx.stroke();
            
        } else if (gameState.currentLevel === 2) { // Revani
            // Golden yellow sponge texture
            dessertCtx.fillStyle = '#e8a83a';
            dessertCtx.fillRect(0, 0, W, H);
            // Crumb sponge dots
            dessertCtx.fillStyle = '#d59424';
            for (let i = 5; i < W; i += 12) {
                for (let j = 5; j < H; j += 12) {
                    if (Math.random() > 0.4) {
                        dessertCtx.fillRect(i + (j%4), j, 2, 2);
                    }
                }
            }
            // Coconut flakes sprinkle
            dessertCtx.fillStyle = 'rgba(255, 255, 255, 0.9)';
            for (let i = 0; i < 400; i++) {
                let rx = (i * 17) % W;
                let ry = (i * 31) % H;
                dessertCtx.fillRect(rx, ry, 2, 1);
            }
        } else { // circular Baklava
            // Golden flaky pastry center circle
            const cx = W/2, cy = H/2, r = 140;
            let grad = dessertCtx.createRadialGradient(cx, cy, 10, cx, cy, r);
            grad.addColorStop(0, '#ffce63');
            grad.addColorStop(0.7, '#e29e2d');
            grad.addColorStop(1, '#ab7211');
            
            dessertCtx.fillStyle = grad;
            dessertCtx.beginPath();
            dessertCtx.arc(cx, cy, r, 0, Math.PI*2);
            dessertCtx.fill();
            
            // Puff pastry layers (concentric faint circular lines)
            dessertCtx.strokeStyle = 'rgba(255,255,255,0.15)';
            dessertCtx.lineWidth = 1.5;
            for (let ir = 20; ir < r; ir += 15) {
                dessertCtx.beginPath();
                dessertCtx.arc(cx, cy, ir, 0, Math.PI*2);
                dessertCtx.stroke();
            }
        }
        
        // Draw garnishes (like pistachio crumbs) inside centroid
        drawSliceGarnish(poly);
        
        // Draw 3D edges inside the cut to give thickness
        dessertCtx.restore();
        
        // Render 3D side walls of cuts
        dessertCtx.save();
        dessertCtx.strokeStyle = '#503517'; // darker sponge cake shadow
        dessertCtx.lineWidth = 2;
        dessertCtx.beginPath();
        dessertCtx.moveTo(poly.vertices[0].x, poly.vertices[0].y);
        for (let i = 1; i < poly.vertices.length; i++) {
            dessertCtx.lineTo(poly.vertices[i].x, poly.vertices[i].y);
        }
        dessertCtx.closePath();
        dessertCtx.stroke();
        dessertCtx.restore();
    });
    
    // 3. Draw Cut Lines (creamy crumbs/reveal gaps)
    dessertCtx.save();
    dessertCtx.strokeStyle = 'rgba(255, 240, 200, 0.4)';
    dessertCtx.lineWidth = 3;
    dessertCtx.shadowColor = '#000';
    dessertCtx.shadowBlur = 2;
    gameState.cutLines.forEach(line => {
        dessertCtx.beginPath();
        dessertCtx.moveTo(line.p1.x, line.p1.y);
        dessertCtx.lineTo(line.p2.x, line.p2.y);
        dessertCtx.stroke();
    });
    dessertCtx.restore();
    
    // 4. Highlight hovered slice if Spatula is selected
    if (gameState.activeTool === 'spatula' && hoverPoly && !gameState.isScooped) {
        dessertCtx.save();
        dessertCtx.strokeStyle = 'rgba(124, 252, 0, 0.7)'; // pistachio green glow
        dessertCtx.lineWidth = 4;
        dessertCtx.beginPath();
        dessertCtx.moveTo(hoverPoly.vertices[0].x, hoverPoly.vertices[0].y);
        for (let i = 1; i < hoverPoly.vertices.length; i++) {
            dessertCtx.lineTo(hoverPoly.vertices[i].x, hoverPoly.vertices[i].y);
        }
        dessertCtx.closePath();
        dessertCtx.stroke();
        
        // Light overlay
        dessertCtx.fillStyle = 'rgba(124, 252, 0, 0.15)';
        dessertCtx.fill();
        dessertCtx.restore();
    }
    
    // 5. Draw active slice trace being dragged/cut
    if (gameState.activeTool === 'knife' && gameState.isDrawingCut) {
        dessertCtx.save();
        dessertCtx.strokeStyle = 'rgba(255, 255, 255, 0.9)';
        dessertCtx.lineWidth = 2.5;
        dessertCtx.setLineDash([5, 5]);
        dessertCtx.beginPath();
        dessertCtx.moveTo(gameState.cutStart.x, gameState.cutStart.y);
        dessertCtx.lineTo(gameState.cutCurrent.x, gameState.cutCurrent.y);
        dessertCtx.stroke();
        
        // Draw projected cut (full extension) to show helper path
        let extended = projectLineToTrayBounds(gameState.cutStart, gameState.cutCurrent, W, H);
        if (extended) {
            dessertCtx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
            dessertCtx.lineWidth = 1;
            dessertCtx.setLineDash([]);
            dessertCtx.beginPath();
            dessertCtx.moveTo(extended.p1.x, extended.p1.y);
            dessertCtx.lineTo(extended.p2.x, extended.p2.y);
            dessertCtx.stroke();
        }
        dessertCtx.restore();
    }
    
    // 6. Draw active particles for ASMR visual feedback
    if (gameState.trayParticles && gameState.trayParticles.length > 0) {
        gameState.trayParticles.forEach(p => {
            dessertCtx.save();
            dessertCtx.fillStyle = p.color;
            dessertCtx.globalAlpha = p.life;
            dessertCtx.beginPath();
            dessertCtx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            dessertCtx.fill();
            dessertCtx.restore();
        });
    }
    
    // 7. Draw target guide outline if player failed the cut
    if (gameState.showCorrectCutGuide && gameState.targetPolygon) {
        dessertCtx.save();
        dessertCtx.strokeStyle = 'rgba(255, 42, 116, 0.85)'; // neon pink glow
        dessertCtx.lineWidth = 3.5;
        dessertCtx.shadowColor = '#ff2a74';
        dessertCtx.shadowBlur = 8;
        dessertCtx.setLineDash([6, 4]);
        dessertCtx.beginPath();
        dessertCtx.moveTo(gameState.targetPolygon[0].x, gameState.targetPolygon[0].y);
        for (let i = 1; i < gameState.targetPolygon.length; i++) {
            dessertCtx.lineTo(gameState.targetPolygon[i].x, gameState.targetPolygon[i].y);
        }
        dessertCtx.closePath();
        dessertCtx.stroke();
        dessertCtx.restore();
    }
}

// --- ASMR PARTICLE SYSTEM ---
function spawnParticles(x, y, count) {
    let colors = [];
    if (gameState.currentLevel === 1) { // Trileçe
        colors = ['#fff6de', '#e28a30', '#c3752e', '#ff2a74']; // sponge, caramel, strawberry/pink highlights
    } else if (gameState.currentLevel === 2) { // Revani
        colors = ['#e8a83a', '#ffffff', '#548d2e', '#ffce63']; // yellow crumb, white coconut, green pistachio
    } else { // Baklava
        colors = ['#ffce63', '#ab7211', '#3c7a1a', '#ffd700']; // flaky golden, dark crust, pistachio green, butter gold
    }
    
    for (let i = 0; i < count; i++) {
        let angle = Math.random() * Math.PI * 2;
        let speed = Math.random() * 3 + 1.5;
        gameState.trayParticles.push({
            x: x,
            y: y,
            vx: Math.cos(angle) * speed + (Math.random() - 0.5) * 1.5,
            vy: Math.sin(angle) * speed - 1.5, // bias upwards
            size: Math.random() * 2.5 + 1.2,
            color: colors[Math.floor(Math.random() * colors.length)],
            life: 1.0,
            decay: Math.random() * 0.04 + 0.03
        });
    }
}

function updateParticles() {
    for (let i = gameState.trayParticles.length - 1; i >= 0; i--) {
        let p = gameState.trayParticles[i];
        p.x += p.vx;
        p.y += p.vy;
        p.vy += 0.12; // gravity
        p.life -= p.decay;
        if (p.life <= 0) {
            gameState.trayParticles.splice(i, 1);
        }
    }
}

let isTrayLoopActive = false;
function startTrayAnimationLoop() {
    if (isTrayLoopActive) return;
    isTrayLoopActive = true;
    function loop() {
        updateParticles();
        drawDessertTray();
        if (gameState.isDrawingCut || (gameState.trayParticles && gameState.trayParticles.length > 0)) {
            requestAnimationFrame(loop);
        } else {
            isTrayLoopActive = false;
        }
    }
    requestAnimationFrame(loop);
}

// Render garnish on top of slices based on type
function drawSliceGarnish(poly) {
    const center = getPolygonCentroid(poly.vertices);
    const area = getPolygonArea(poly.vertices);
    if (area < 800) return; // Slice too small for garnish
    
    dessertCtx.save();
    
    if (gameState.currentLevel === 1) { // Trileçe: Pistachio sprinkles on corners or center
        dessertCtx.fillStyle = '#4b832b'; // Dark pistachio green
        dessertCtx.beginPath();
        dessertCtx.arc(center.x, center.y, 6, 0, Math.PI * 2);
        dessertCtx.fill();
        
        // Spiced flakes
        dessertCtx.fillStyle = '#6fa442';
        for (let i = 0; i < 8; i++) {
            let angle = (i/8) * Math.PI * 2;
            dessertCtx.fillRect(center.x + Math.cos(angle)*8 - 1, center.y + Math.sin(angle)*8 - 1, 2, 2);
        }
    } else if (gameState.currentLevel === 2) { // Revani: Pistachio nut in center
        dessertCtx.fillStyle = '#548d2e';
        dessertCtx.beginPath();
        dessertCtx.ellipse(center.x, center.y, 8, 5, Math.PI / 4, 0, Math.PI * 2);
        dessertCtx.fill();
        dessertCtx.fillStyle = '#fffdd0'; // coconut flakes on garnish
        dessertCtx.fillRect(center.x - 2, center.y - 1, 3, 2);
    } else { // circular Baklava: Pistachio powder on top of center
        dessertCtx.fillStyle = '#3c7a1a';
        // Draw scattered pistachio powder circle
        for (let i = 0; i < 25; i++) {
            let angle = Math.random() * Math.PI * 2;
            let radius = Math.random() * 12;
            dessertCtx.fillRect(center.x + Math.cos(angle)*radius, center.y + Math.sin(angle)*radius, 2, 2);
        }
    }
    
    dessertCtx.restore();
}

// Draw the slice polygon on spatula (when scooped)
function renderSpatulaSlice(ctx, polyVertices, mx, my) {
    // Determine bounds and draw polygon centered/aligned on spatula
    const centroid = getPolygonCentroid(polyVertices);
    
    ctx.save();
    ctx.translate(mx - 30, my - 60); // Offset to sit on top of spatula blade
    ctx.scale(0.7, 0.7); // scale down slightly for aesthetic fit
    ctx.translate(-centroid.x, -centroid.y);
    
    // Draw polygon base shape on spatula
    ctx.beginPath();
    ctx.moveTo(polyVertices[0].x, polyVertices[0].y);
    for (let i = 1; i < polyVertices.length; i++) {
        ctx.lineTo(polyVertices[i].x, polyVertices[i].y);
    }
    ctx.closePath();
    
    // Render cake slice textures
    ctx.shadowColor = 'rgba(0,0,0,0.4)';
    ctx.shadowBlur = 8;
    ctx.shadowOffsetY = 10;
    
    ctx.clip();
    
    if (gameState.currentLevel === 1) {
        ctx.fillStyle = '#fff6de';
        ctx.fillRect(0, 0, W*2, H*2);
        let grad = ctx.createLinearGradient(0, 0, W, H);
        grad.addColorStop(0, '#c3752e'); grad.addColorStop(1, '#944b0f');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, W*2, H*2);
        
        ctx.strokeStyle = 'rgba(255,255,255,0.7)';
        ctx.lineWidth = 4;
        ctx.beginPath();
        for (let x = -50; x < W + 50; x += 30) {
            ctx.moveTo(x, -50);
            ctx.bezierCurveTo(x + 15, H/2, x - 15, H/2, x, H + 50);
        }
        ctx.stroke();
    } else if (gameState.currentLevel === 2) {
        ctx.fillStyle = '#e8a83a';
        ctx.fillRect(0, 0, W*2, H*2);
        ctx.fillStyle = '#rgba(255,255,255,0.8)';
        for (let i = 0; i < 100; i++) {
            ctx.fillRect(Math.random()*W, Math.random()*H, 2, 2);
        }
    } else {
        ctx.fillStyle = '#ffce63';
        ctx.fillRect(0, 0, W*2, H*2);
    }
    
    // Garnish
    ctx.fillStyle = '#4b832b';
    ctx.beginPath();
    ctx.arc(centroid.x, centroid.y, 8, 0, Math.PI * 2);
    ctx.fill();
    
    ctx.restore();
}


// --- SLICING ENGINE LOGIC ---

// Reset current tray and initialize polygon state
function resetDessertTray() {
    gameState.trayPolygons = [];
    gameState.cutLines = [];
    gameState.trayParticles = []; // Clear particles
    gameState.polygonIdCounter = 0;
    gameState.servedSliceId = null;
    gameState.isScooped = false;
    
    if (gameState.currentLevel === 3) {
        // Circle Baklava tray: Start with circular polygon of radius 140 centered at W/2, H/2
        const cx = W/2, cy = H/2, r = 140;
        let circleVertices = generateCirclePolygon(cx, cy, r, 32);
        gameState.trayPolygons.push({
            id: gameState.polygonIdCounter++,
            vertices: circleVertices
        });
    } else {
        // Rectangle trays (Trileçe, Revani): 0,0 to W,H
        gameState.trayPolygons.push({
            id: gameState.polygonIdCounter++,
            vertices: [
                {x: 0, y: 0},
                {x: W, y: 0},
                {x: W, y: H},
                {x: 0, y: H}
            ]
        });
    }
    
    drawDessertTray();
}

// Slice the tray along a line segment
function makeTraySlice(p1, p2) {
    let extended = projectLineToTrayBounds(p1, p2, W, H);
    if (!extended) return;
    
    let newPolygons = [];
    let splitOccurred = false;
    
    gameState.trayPolygons.forEach(poly => {
        let splitResult = splitPolygon(poly.vertices, extended.p1, extended.p2);
        if (splitResult) {
            newPolygons.push({
                id: gameState.polygonIdCounter++,
                vertices: splitResult[0]
            });
            newPolygons.push({
                id: gameState.polygonIdCounter++,
                vertices: splitResult[1]
            });
            splitOccurred = true;
        } else {
            newPolygons.push(poly);
        }
    });
    
    if (splitOccurred) {
        gameState.trayPolygons = newPolygons;
        gameState.cutLines.push(extended);
        audio.playSlice();
        drawDessertTray();
    }
}


// --- SCORING & INTERSECTION OVER UNION (IoU) ---

// Approximate polygon Intersection over Union (IoU) using point sampling (Grid of 28 x 16 = 448 points)
function calculateAccuracy(servedVertices, targetVertices) {
    let intersectionPoints = 0;
    let unionPoints = 0;
    
    // Bounds of sampling: WxH
    for (let x = 10; x < W; x += 20) {
        for (let y = 10; y < H; y += 20) {
            let pt = {x: x, y: y};
            let inServed = isPointInPolygon(pt, servedVertices);
            let inTarget = isPointInPolygon(pt, targetVertices);
            
            if (inServed && inTarget) {
                intersectionPoints++;
            }
            if (inServed || inTarget) {
                unionPoints++;
            }
        }
    }
    
    if (unionPoints === 0) return 0;
    return Math.round((intersectionPoints / unionPoints) * 100);
}


// --- CUSTOMER QUEUE STATE MACHINE & DIALOGUE ---

// Load next customer in queue
function spawnCustomer() {
    if (gameState.customerIndex >= gameState.customerMax) {
        // End of the day!
        endDayReport();
        return;
    }
    
    // Pick profile
    const profileIndex = gameState.customerIndex % CUSTOMER_PROFILES.length;
    gameState.customerData = CUSTOMER_PROFILES[profileIndex];
    
    // Change background image dynamically to show different Turkish historic cities
    const BACKGROUNDS = [
        'assets/shop_background.png',  // Istanbul
        'assets/bg_cappadocia.png',    // Kapadokya
        'assets/bg_safranbolu.png',    // Safranbolu
        'assets/bg_mardin.png'         // Mardin
    ];
    const bgIndex = gameState.customerIndex % BACKGROUNDS.length;
    document.getElementById("street-view").style.backgroundImage = `url('${BACKGROUNDS[bgIndex]}')`;
    
    // Set UI
    const customerArea = document.getElementById("customer-area");
    customerArea.innerHTML = gameState.customerData.avatar;
    customerArea.className = "entering";
    
    gameState.customerState = 'entering';
    
    // Wait for slide-in animation, then trigger knocking & speech
    setTimeout(() => {
        customerArea.className = "active";
        triggerCustomerIntro();
    }, 600);
}

function getCustomerDialogue(profile, level, bgIndex) {
    const dialects = {
        0: { // Istanbul
            "Emre": {
                1: "Selamlar usta! Şöyle tam dikey ortadan güzel bir dilim kesebilir misin? Yarısını bana ver gerisi tezgaha.",
                2: "Usta kolay gelsin, tatlıların nefis görünüyor. Bana çaprazından büyük bir dilim keser misin?",
                3: "Hayırlı işler! Baklavanın çıtırlığı harika. Şöyle 8 dilim yapıp birini bana verir misin?"
            },
            "Kerem": {
                1: "Usta selamlar! Yazılım kodlarken canım çok tatlı çekti. Şuradan küçük bir kare dilim alabilir miyim?",
                2: "Selam usta! Revaniyi çok severim. Bana şöyle şık bir eşkenar dilim kesiver hele.",
                3: "Kolay gelsin usta! Şerbetli fıstıklı baklavanın göbeğinden bana küçük bir dilim verir misin?"
            },
            "Yeni Evliler": {
                1: "Selamlar usta! Düğünümüzden çıktık, ağzımız tatlansın diye geldik! Bize şöyle büyük bir yarım dilim kesebilir misin?",
                2: "Usta hayırlı işler! En mutlu günümüzde bize şık bir baklava/eşkenar dilim kesip verir misin?",
                3: "Selamlar usta! Düğün bitti, şimdi tatlı zamanı! Bize baklavanın tam ortasındaki o nefis yuvarlak göbeği çıkarır mısın?"
            }
        },
        1: { // Cappadocia
            "Emre": {
                1: "N'örüyon usta! Gadanı alıyım, şurdan tam dikey ortasından bölesin de, yarısını bana veresin hele.",
                2: "Kolay gelsin hemşerim! Şööle çaprazından gözel bi dilim kesiver hele.",
                3: "Hayırlı işler! Baklavayı sekiz bölesin de, bir dadlı dilimini bana veresin gadanı alıyım."
            },
            "Kerem": {
                1: "Usta n'örüyon! Bilgisayar başında canım tatlı çekti. Şuradan ufak bi kare dilim kesiver hele.",
                2: "Kolay gelsin evlat! Şööle baklava dilimi gibi şık bi parça kesiver bakayun.",
                3: "Hayırlı işler görüyong mu! Baklavanın göbeğindeki o daireyi yuvarlak kesip veresing ha!"
            },
            "Yeni Evliler": {
                1: "N'örüyon usta! Düğünden çıktık geldik, ağzımız dadlansın. Şurdan dikey ortadan kesiver hele.",
                2: "Kolay gelsin evlat! Düğün hatırına şööle çaprazından böyük bi dilim alalım.",
                3: "Hayırlı işler görüyong mu! Düğün bitti, baklavanın tam göbeğindeki daireyi yuvarlak kesip veresing!"
            }
        },
        2: { // Safranbolu
            "Emre": {
                1: "Selamün aleyküm usta bba! Cama çizdüm bak, şuradan dikey kesüver de yarısını alayum.",
                2: "Kolay gelsün usta! Şuradan çapraz kesüver de görelüm bakayun.",
                3: "Hayırlı işler usta! Baklavayı sekiz dilim yapasun da birini vir hele bba."
            },
            "Kerem": {
                1: "Selamün aleyküm bba! Kod yazarken canum çekti. Şuradan ufak bir kare dilim virüver bakayun.",
                2: "Kolay gelsün usta! Bana 4 tane baklava dilimi çıkarüver hemen bba.",
                3: "Hayırlı işler usta! Baklavanın göbeğindeki daireyi yuvarlak kesüverüceksün de bana vireceksün!"
            },
            "Yeni Evliler": {
                1: "Selamün aleyküm usta bba! Düğünden geldük, ağzumuz tatlansun. Şuradan dikey kesüver de yarısını alalum.",
                2: "Kolay gelsün usta! En mutlu günümüzde bize şık bir baklava dilimi kesiver hele.",
                3: "Hayırlı işler usta! Düğün bitti, baklavanın göbeğindeki daireyi yuvarlak kesüverüceksün de vürüceksün!"
            }
        },
        3: { // Mardin
            "Emre": {
                1: "Selamın aleykum keke! Başım gözüm üstüne, hele şu tatlıyı tam dikey ortadan kes, sol tarafı bize veresin.",
                2: "Gözümün nuru kolay gelsin! Bize şuradan çapraz büyük dilim keseceksen veresin valla.",
                3: "Hayırlı işler keke! Baklavayı 8 dilim yapasan, bir dilimini hemen bize veresin başım gözüm üstüne."
            },
            "Kerem": {
                1: "Selamın aleykum usta! Yazılım yazarken canımız çekti valla, bize şuradan küçük bir kare dilim veresin.",
                2: "Gözümün nuru kolay gelsin! Bize 4 tane şık baklava dilimi çıkarasan görelim.",
                3: "Hayırlı işler keke! Baklavanın tam ortasındaki dairesel göbek kısmını yuvarlak kesip veresin valla."
            },
            "Yeni Evliler": {
                1: "Selamın aleykum keke! Düğünümüzden çıktık geldik, ağzımız tatlansın. Hele şu tatlıyı tam dikey ortadan kesiveresin.",
                2: "Gözümün nuru kolay gelsin! En mutlu günümüzde bize şuradan çapraz büyük dilim kesip veresin valla.",
                3: "Hayırlı işler keke! Düğün bitti, baklavanın tam ortasındaki o dairesel göbek kısmını yuvarlak kesip bize veresin."
            }
        }
    };
    
    return dialects[bgIndex][profile.name][level];
}

function getAngryFeedback(profile, bgIndex) {
    const angryDialects = {
        0: { // Istanbul
            "Emre": "Bu ne biçim kesim birader? Dilim mahvolmuş!",
            "Kerem": "Usta bu kesimde bariz bug var, hiç olmamış!",
            "Yeni Evliler": "Aşkım bu kesim hiç olmamış, usta tatlımızı mahvetti!"
        },
        1: { // Cappadocia
            "Emre": "Gözün nere bakıyodu usta? Bööle yamuk yumuk kesilir mi yav, batırmışsın tatlıyı!",
            "Kerem": "N'örüyon usta! Yamuk kesmişsing, hiç gözel olmamış, beğenmedim yav!",
            "Yeni Evliler": "Usta n'örüyon! Düğün günümüzde bu yamuk kesim hiç yakıştı mı yav?"
        },
        2: { // Safranbolu
            "Emre": "Ula bu ne biçim iş bba! Eğrü büğrü kesmişsün, hiç begenmedüm!",
            "Kerem": "Hacan bu nasıl kesim usta! Hiç becerememişsün, rezalettür!",
            "Yeni Evliler": "Ula usta bba! Düğün günümüzde bu eğri büğrü kesim hiç oldu mu bakayun?"
        },
        3: { // Mardin
            "Emre": "Yahu keke, bu ne biçim kesimdir? Yamuk kesmişsen, başımı ağrıttın valla!",
            "Kerem": "Rezalettir valla keke! Kesimin berbattır, hiç heyri yoktur bunun!",
            "Yeni Evliler": "Yahu keke, bu mutlu günümüzde bu berbat kesim hiç oldu mu valla?"
        }
    };
    
    return angryDialects[bgIndex][profile.name];
}

function getFeedbackDialogue(profile, acc, bgIndex) {
    if (acc < 40) {
        return getAngryFeedback(profile, bgIndex);
    }
    
    const dialects = {
        0: { // Istanbul
            "Emre": {
                90: "Muhteşem! Kesim harika, tam istediğim gibi! Teşekkürler.",
                70: "Fena değil, idare eder. Ellerin dert görmesin usta.",
                40: "Biraz yamuk kesmişsin sanki ama neyse, karnım aç..."
            },
            "Kerem": {
                90: "Kusursuz! Bug yok, tertemiz sıfır hata kesmişsin. Helal!",
                70: "Kabul edilebilir bir kesim. Kod derlendi ama optimize edilebilir.",
                40: "Simetride bariz hatalar var ama lezzeti kurtarıyor."
            },
            "Yeni Evliler": {
                90: "Mükemmel kesim! Tatlı gibi tatlı, ellerine sağlık usta!",
                70: "Harika usta, ağzımız tatlandı. Çok teşekkür ederiz.",
                40: "Biraz yamuk olmuş ama neyse usta, düğün telaşına sayalım."
            }
        },
        1: { // Cappadocia
            "Emre": {
                90: "Ooo, gadanı alıyım usta! Pek gözel kesmişsing, ellerine sağlık!",
                70: "İdare eder usta, fena değil. Sağ olasın.",
                40: "Biraz yamuk olmuş emme neyse usta, karnımız aç."
            },
            "Kerem": {
                90: "Nefis! Tam ölçüsünde kesmişsing, sıfır hata olmuş!",
                70: "İdare eder, fena kesmemişsing. İş görür.",
                40: "Yamuk yumuk olmuş usta, elinin ayarı hiç gözel değil emme neyse."
            },
            "Yeni Evliler": {
                90: "Ooo usta gadanı alalım! Harika bi dilim verdin, çok yaşa!",
                70: "Gözel olmuş usta, ellerin dert görmesin.",
                40: "Biraz yamuk kesmişsin emme düğün hatırına kabulümüzdür."
            }
        },
        2: { // Safranbolu
            "Emre": {
                90: "Aferün usta bba! Kesüm harika olmış, tam istediğüm gibi!",
                70: "Fena değül, iş görür bba. Sağ olasıca.",
                40: "Eğrü kesmişsün biraz emme neyse vir bakayun."
            },
            "Kerem": {
                90: "Harikulade! Kesüm cetvel gibi olmış bba, aferün!",
                70: "Fena sayılmaz usta, idare edüverür hacan.",
                40: "Yamuk kesmişsün bba, hiç ölçememişsün emme neyse."
            },
            "Yeni Evliler": {
                90: "Usta bba, harika kesmişsün! Eline koluna sağlık pazar pazar!",
                70: "Çok güzel bba, ağzumuz tatlandı, sağ olasıca.",
                40: "Eğri büğrü olmuş usta bba emme neyse yiyeceğiz artık."
            }
        },
        3: { // Mardin
            "Emre": {
                90: "Maşallah keke! Kesimin mükemmeldir valla, ellerin dert görmesin!",
                70: "Fena değildir keke, başım gözüm üstüne, sağ olasın.",
                40: "Hele biraz yamuktur keke, ama neyse ver gitsin."
            },
            "Kerem": {
                90: "Valahi helal olsun! Kesimin bir sanattır keke, tebrik ederim.",
                70: "Fena değildir valla, kabulümüzdür keke.",
                40: "Simetriyi bozmuşsan keke valla, ama neyse başım gözüm üstüne."
            },
            "Yeni Evliler": {
                90: "Başımız gözümüz üstüne keke! Harika bir kesimdir, düğünümüze layık valla!",
                70: "Çok güzeldir keke, ellerin dert görmesin, sağ olasın.",
                40: "Yamuktur keke valla, ama neyse mutlu günümüzdür, helal olsun."
            }
        }
    };
    
    let scoreBracket = 40;
    if (acc >= 90) scoreBracket = 90;
    else if (acc >= 70) scoreBracket = 70;
    
    return dialects[bgIndex][profile.name][scoreBracket];
}

// Speak and show dialog
function triggerCustomerIntro() {
    audio.playKnock();
    
    // Fog opacity regenerates a bit
    fogOpacity = 0.85;
    drawFog();
    
    // Speech bubble settings
    const bubble = document.getElementById("dialogue-bubble");
    const text = document.getElementById("dialogue-text");
    const hint = document.getElementById("order-hint");
    
    const bgIndex = gameState.customerIndex % 4;
    text.innerHTML = getCustomerDialogue(gameState.customerData, gameState.currentLevel, bgIndex);
    
    // Set text hint based on shape
    let hintStr = "";
    if (gameState.currentLevel === 1) {
        hintStr = gameState.customerIndex === 0 ? "Kare/Yarım Kesim" : (gameState.customerIndex === 1 ? "Köşeden Kare" : "Üçgen Kesim");
    } else if (gameState.currentLevel === 2) {
        hintStr = gameState.customerIndex === 0 ? "Büyük Çapraz" : (gameState.customerIndex === 1 ? "Eşkenar Dilim" : "Baklava Dilimi");
    } else {
        hintStr = gameState.customerIndex === 0 ? "Radyal Wedge (Daire)" : (gameState.customerIndex === 1 ? "Dilim Wedge" : "Göbek/Daire Kesim");
    }
    hint.innerHTML = `Tarif Edilen Şekil: ${hintStr}`;
    
    bubble.className = "glass-panel active";
    gameState.customerState = 'talking';
    
    // Set customer container talking class
    const customerArea = document.getElementById("customer-area");
    customerArea.className = "active talking";
    
    // Trigger spoken dialogue voice
    audio.speakDialogue(text.innerHTML, "tr-TR");
    
    // Set target cuts & shape inside customer logic
    const drawSteps = gameState.customerData.setupTarget(gameState.currentLevel);
    
    // Trigger drawing demo on foggy window after 2.5s of talking
    setTimeout(() => {
        animateCustomerDrawing(drawSteps);
    }, 2500);
}

// Animate drawing lines on foggy window (showing customer gestures)
function animateCustomerDrawing(drawSteps) {
    gameState.customerState = 'drawing';
    
    const customerArea = document.getElementById("customer-area");
    customerArea.className = "active drawing";
    
    // Create customer hand element dynamically if not present
    let customerHandEl = document.getElementById("customer-hand");
    if (!customerHandEl) {
        customerHandEl = document.createElement("div");
        customerHandEl.id = "customer-hand";
        customerHandEl.style.position = "absolute";
        customerHandEl.style.width = "48px";
        customerHandEl.style.height = "48px";
        customerHandEl.style.pointerEvents = "none";
        customerHandEl.style.zIndex = "8";
        customerHandEl.style.display = "none";
        customerHandEl.style.filter = "drop-shadow(2px 5px 6px rgba(0,0,0,0.5))";
        customerHandEl.style.transform = "translate(-12px, -8px)"; // Align tip of index finger
        customerHandEl.innerHTML = `
            <svg viewBox="0 0 32 32" width="100%" height="100%">
                <!-- Back of hand with index finger pointing up -->
                <path d="M14 6 L14 18 A 2 2 0 0 0 18 18 L18 6 A 2 2 0 0 1 22 6 L22 18 A 2 2 0 0 0 26 18 L26 10 A 2 2 0 0 1 30 10 L30 22 C 30 28 24 32 18 32 L10 32 C 4 32 0 28 0 22 L0 14 A 2 2 0 0 1 4 14 L4 18 A 2 2 0 0 0 8 18 L8 2 A 2 2 0 0 1 12 2 L12 18 A 2 2 0 0 0 14 18 Z" fill="#fcd1a1" stroke="#2b1a0e" stroke-width="1.5"/>
            </svg>
        `;
        document.getElementById("street-view").appendChild(customerHandEl);
    }
    
    // Create dynamic arm SVG overlay if not present
    let customerArmSvg = document.getElementById("customer-arm-svg");
    if (!customerArmSvg) {
        customerArmSvg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        customerArmSvg.id = "customer-arm-svg";
        customerArmSvg.setAttribute("style", "position:absolute; inset:0; pointer-events:none; z-index:7;");
        document.getElementById("street-view").appendChild(customerArmSvg);
    }
    customerArmSvg.style.display = "block";
    
    // Configure arm skin/sleeve colors
    let sleeveColor = "#f5ebd6"; // Emre beige
    let skinColor = "#eed1b7";
    if (gameState.customerData) {
        if (gameState.customerData.name === "Kerem") {
            sleeveColor = "#3a6fb3"; // Kerem blue
            skinColor = "#fcd1a1";
        } else if (gameState.customerData.name === "Yeni Evliler") {
            sleeveColor = "#ffffff"; // Bride white lace
            skinColor = "#fcd1a1";
        }
    }
    
    const banner = document.getElementById("instruction-banner");
    const bannerText = document.getElementById("instruction-text");
    bannerText.innerHTML = "Müşteri cama çiziyor, el hareketlerini izle...";
    banner.style.display = "block";
    
    let stepIdx = 0;
    let progress = 0;
    
    function drawAnimationFrame() {
        if (stepIdx >= drawSteps.length) {
            // Drawing is complete! Hide hand and arm
            customerHandEl.style.display = "none";
            customerArmSvg.style.display = "none";
            
            customerArea.className = "active";
            
            bannerText.innerHTML = "Kesim yap! Dilimi spatula ile servis et.";
            gameState.customerState = 'waiting';
            
            // Faint red guidelines remain on glass window
            drawFogGuidelines(drawSteps);
            return;
        }
        
        const step = drawSteps[stepIdx];
        
        // Linear interpolate coordinates from step.p1 to step.p2
        const glassWidth = glassCanvas.width;
        const glassHeight = glassCanvas.height;
        
        // Map function: W -> center of glass canvas
        const mapX = (x) => ((x / W) * (glassWidth * 0.6)) + (glassWidth * 0.2);
        const mapY = (y) => ((y / H) * (glassHeight * 0.6)) + (glassHeight * 0.25);
        
        let startX = mapX(step.p1.x);
        let startY = mapY(step.p1.y);
        let endX = mapX(step.p2.x);
        let endY = mapY(step.p2.y);
        
        let currX = startX + (endX - startX) * progress;
        let currY = startY + (endY - startY) * progress;
        
        // Update hand position
        customerHandEl.style.left = `${currX}px`;
        customerHandEl.style.top = `${currY}px`;
        customerHandEl.style.display = "block";
        
        // Update arm SVG paths
        let shoulderX = glassWidth / 2 + 30; // right shoulder of character
        let shoulderY = glassHeight - 30;
        if (gameState.customerData.name === "Yeni Evliler") {
            shoulderX = glassWidth / 2 - 20; // Bride is on left side of couple
        }
        
        let wristX = currX;
        let wristY = currY + 28;
        
        // Elbow bend offset calculation
        let cpX = (shoulderX + wristX) / 2;
        let cpY = (shoulderY + wristY) / 2 + 50;
        if (wristX < shoulderX) {
            cpX = Math.min(shoulderX, wristX) - 60;
        } else {
            cpX = Math.max(shoulderX, wristX) + 60;
        }
        
        let sleevePath = document.getElementById("arm-sleeve");
        let wristPath = document.getElementById("arm-wrist");
        
        if (!sleevePath) {
            sleevePath = document.createElementNS("http://www.w3.org/2000/svg", "path");
            sleevePath.id = "arm-sleeve";
            sleevePath.setAttribute("fill", "none");
            sleevePath.setAttribute("stroke-linecap", "round");
            sleevePath.setAttribute("stroke-linejoin", "round");
            customerArmSvg.appendChild(sleevePath);
        }
        if (!wristPath) {
            wristPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
            wristPath.id = "arm-wrist";
            wristPath.setAttribute("fill", "none");
            wristPath.setAttribute("stroke-linecap", "round");
            customerArmSvg.appendChild(wristPath);
        }
        
        sleevePath.setAttribute("stroke", sleeveColor);
        sleevePath.setAttribute("stroke-width", "26");
        sleevePath.setAttribute("d", `M ${shoulderX} ${shoulderY} Q ${cpX} ${cpY} ${wristX} ${wristY}`);
        
        wristPath.setAttribute("stroke", skinColor);
        wristPath.setAttribute("stroke-width", "20");
        
        let dx = wristX - cpX;
        let dy = wristY - cpY;
        let len = Math.sqrt(dx*dx + dy*dy);
        let ux = dx / (len || 1);
        let uy = dy / (len || 1);
        let skinStartX = wristX - ux * 8;
        let skinStartY = wristY - uy * 8;
        wristPath.setAttribute("d", `M ${skinStartX} ${skinStartY} L ${wristX} ${wristY}`);
        
        // Clear fog at current finger location
        clearFogTrace(currX, currY, 18);
        
        // Draw faint red sketch path
        glassCtx.save();
        glassCtx.strokeStyle = 'rgba(255, 42, 116, 0.4)';
        glassCtx.lineWidth = 4;
        glassCtx.beginPath();
        glassCtx.moveTo(startX, startY);
        glassCtx.lineTo(currX, currY);
        glassCtx.stroke();
        glassCtx.restore();
        
        progress += 0.05; // speed of drawing
        if (progress >= 1.0) {
            stepIdx++;
            progress = 0;
        }
        
        requestAnimationFrame(drawAnimationFrame);
    }
    
    requestAnimationFrame(drawAnimationFrame);
}

// Keep trace guidelines visible after customer finishes drawing
function drawFogGuidelines(drawSteps) {
    const glassWidth = glassCanvas.width;
    const glassHeight = glassCanvas.height;
    const mapX = (x) => ((x / W) * (glassWidth * 0.6)) + (glassWidth * 0.2);
    const mapY = (y) => ((y / H) * (glassHeight * 0.6)) + (glassHeight * 0.25);
    
    glassCtx.save();
    glassCtx.strokeStyle = 'rgba(255, 42, 116, 0.25)';
    glassCtx.lineWidth = 3;
    glassCtx.setLineDash([4, 4]);
    drawSteps.forEach(step => {
        glassCtx.beginPath();
        glassCtx.moveTo(mapX(step.p1.x), mapY(step.p1.y));
        glassCtx.lineTo(mapX(step.p2.x), mapY(step.p2.y));
        glassCtx.stroke();
    });
    glassCtx.restore();
}

// Serve the scooped piece and evaluate accuracy
function serveSliceToCustomer(polyVertices) {
    if (gameState.customerState !== 'waiting') return;
    
    gameState.customerState = 'serving';
    
    // Hide serving tray plate
    const trayPlate = document.getElementById("serving-tray-plate");
    trayPlate.className = "";
    
    // 1. Calculate accuracy score
    const acc = calculateAccuracy(polyVertices, gameState.targetPolygon);
    
    // Add to daily average tracker
    gameState.dayAccuracySum += acc;
    gameState.dayAccuracyCount++;
    
    // Calculate tips based on accuracy
    let basePrice = 5.00;
    let tip = 0;
    let ratingText = "";
    
    const bgIndex = gameState.customerIndex % 4;
    ratingText = getFeedbackDialogue(gameState.customerData, acc, bgIndex);
    
    if (acc >= 70) {
        audio.playSuccess();
        if (acc >= 90) {
            tip = Math.random() * 2 + 1.5;
        } else {
            tip = Math.random() * 1;
        }
        createTipFloatingText(tip);
    } else {
        if (acc >= 40) {
            tip = 0.10;
            audio.playKnock();
        } else {
            tip = 0.00;
            audio.playFail();
        }
    }
    
    let totalCash = basePrice + tip;
    gameState.cash += totalCash;
    gameState.tipsEarned += tip;
    
    // Display customer response
    const text = document.getElementById("dialogue-text");
    text.innerHTML = `<strong>Doğruluk: %${acc}</strong><br>"${ratingText}"`;
    
    // Determine dynamic delay: show guide for longer if they failed
    const failed = acc < 70;
    
    const customerArea = document.getElementById("customer-area");
    if (failed) {
        customerArea.className = "active angry";
        gameState.showCorrectCutGuide = true;
        // Append helper text in dialogue
        text.innerHTML += `<br><span style="color: var(--neon-pink); font-size: 0.85rem; font-weight:800;">[DOĞRU KESİM TEPSİDE GÖSTERİLİYOR]</span>`;
        drawDessertTray();
    } else {
        customerArea.className = "active happy";
    }
    
    let evaluationDelay = failed ? 5800 : 3500;
    
    // Speak response (speed/pitch shifted if angry)
    if (failed && window.speechSynthesis) {
        window.speechSynthesis.cancel();
        const cleanText = ratingText.replace(/<[^>]*>/g, '');
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = 'tr-TR';
        
        // Find voice
        const voices = window.speechSynthesis.getVoices();
        const langVoices = voices.filter(v => v.lang.startsWith('tr'));
        
        // Make TTS sound faster and angrier
        utterance.rate = 1.15; // Speed up speech
        
        if (gameState.customerData.name === "Emre") {
            utterance.pitch = 0.8; // Deep heated pitch
            const male = langVoices.find(v => v.name.toLowerCase().includes('male') || v.name.toLowerCase().includes('tolga'));
            if (male) utterance.voice = male;
        } else if (gameState.customerData.name === "Kerem") {
            utterance.pitch = 0.75; // Lower gamer growl pitch
            const male = langVoices.find(v => v.name.toLowerCase().includes('male') || v.name.toLowerCase().includes('tolga'));
            if (male) utterance.voice = male;
        } else if (gameState.customerData.name === "Yeni Evliler") {
            utterance.pitch = 0.95; // Fretful pitch
            const female = langVoices.find(v => v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('yelda'));
            if (female) utterance.voice = female;
        }
        
        audio.setVolume(0.15);
        utterance.onend = () => audio.setVolume(0.4);
        utterance.onerror = () => audio.setVolume(0.4);
        window.speechSynthesis.speak(utterance);
    } else {
        // Regular happy speech
        audio.speakDialogue(ratingText, 'tr-TR');
    }
    
    let totalCashDummy = totalCash; // dummy assignment to keep block matches
    
    // Remove the served slice from tray
    gameState.trayPolygons = gameState.trayPolygons.filter(p => p.id !== gameState.servedSliceId);
    gameState.servedSliceId = null;
    gameState.isScooped = false;
    drawDessertTray();
    
    // Trigger customer departure
    setTimeout(() => {
        const customerArea = document.getElementById("customer-area");
        customerArea.className = "leaving";
        document.getElementById("dialogue-bubble").className = "glass-panel";
        
        // Hide guidelines guide
        gameState.showCorrectCutGuide = false;
        drawDessertTray();
        
        setTimeout(() => {
            customerArea.innerHTML = "";
            gameState.customerIndex++;
            spawnCustomer();
        }, 600);
    }, evaluationDelay);
}

// Generate tip float text animation
function createTipFloatingText(tipVal) {
    if (tipVal <= 0) return;
    const label = document.createElement("div");
    label.className = "floating-tip";
    label.innerText = `+$${tipVal.toFixed(2)} Bahşiş!`;
    
    // Center of game screen
    label.style.left = "50%";
    label.style.top = "50%";
    
    document.getElementById("game-wrapper").appendChild(label);
    
    setTimeout(() => {
        label.remove();
    }, 1200);
}


// --- INTERACTIVITY & CONTROLS ---

let hoverPoly = null; // tracking which polygon is highlighted by spatula mouse hover
let mouseOnTray = false;

// Handle mouse movements on dessert canvas (for slice highlight and tool render)
function handleDessertMouseMove(e) {
    const rect = dessertCanvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    
    const currPos = {x: mx, y: my};
    
    // Calculate drag velocity for ASMR audio pitch modulation
    if (gameState.isDrawingCut && gameState.activeTool === 'knife') {
        let dragDist = dist(currPos, gameState.lastMousePos);
        audio.updateContinuousSlice(dragDist);
        
        // Spawn crumbs particles during slice drag
        if (dragDist > 1.5) {
            spawnParticles(mx, my, Math.min(Math.floor(dragDist / 3.0) + 1, 3));
            startTrayAnimationLoop();
        }
    }
    gameState.lastMousePos = currPos;
    
    gameState.cutCurrent = {x: mx, y: my};
    
    // Position active overlay tool
    const overlay = document.getElementById("fps-tool-overlay");
    const wrapRect = document.getElementById("game-wrapper").getBoundingClientRect();
    
    overlay.style.left = `${e.clientX - wrapRect.left}px`;
    overlay.style.top = `${e.clientY - wrapRect.top}px`;
    
    // Highlight slice under spatula
    if (gameState.activeTool === 'spatula' && !gameState.isScooped) {
        let found = null;
        gameState.trayPolygons.forEach(poly => {
            if (isPointInPolygon({x: mx, y: my}, poly.vertices)) {
                found = poly;
            }
        });
        
        if (hoverPoly !== found) {
            hoverPoly = found;
            drawDessertTray();
        }
    } else {
        hoverPoly = null;
    }
    
    if (gameState.isDrawingCut && gameState.activeTool === 'knife') {
        drawDessertTray();
    }
}

// Mouse events on dessert tray
dessertCanvas.addEventListener("mouseenter", () => {
    mouseOnTray = true;
    document.getElementById("fps-tool-overlay").className = "active";
});

dessertCanvas.addEventListener("mouseleave", () => {
    mouseOnTray = false;
    document.getElementById("fps-tool-overlay").className = "";
    if (gameState.isDrawingCut) {
        gameState.isDrawingCut = false;
        audio.stopContinuousSlice();
    }
    drawDessertTray();
});

dessertCanvas.addEventListener("mousemove", handleDessertMouseMove);

dessertCanvas.addEventListener("mousedown", (e) => {
    const rect = dessertCanvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    
    if (gameState.activeTool === 'knife') {
        // Start cut line drawing
        gameState.isDrawingCut = true;
        gameState.cutStart = {x: mx, y: my};
        gameState.cutCurrent = {x: mx, y: my};
        gameState.lastMousePos = {x: mx, y: my};
        audio.startContinuousSlice();
    } else if (gameState.activeTool === 'spatula' && !gameState.isScooped) {
        // Try scoop piece under mouse
        let found = null;
        gameState.trayPolygons.forEach(poly => {
            if (isPointInPolygon({x: mx, y: my}, poly.vertices)) {
                found = poly;
            }
        });
        
        if (found) {
            gameState.servedSliceId = found.id;
            gameState.isScooped = true;
            audio.playScoop();
            
            // Switch image on FPS display spatula
            document.getElementById("fps-spatula-img").style.display = "block";
            // Highlight serving tray plate in bar
            const trayPlate = document.getElementById("serving-tray-plate");
            trayPlate.className = "active";
            
            drawDessertTray();
        }
    }
});

dessertCanvas.addEventListener("mouseup", (e) => {
    if (gameState.activeTool === 'knife' && gameState.isDrawingCut) {
        const rect = dessertCanvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        
        audio.stopContinuousSlice();
        
        // Execute split slicing
        makeTraySlice(gameState.cutStart, {x: mx, y: my});
        gameState.isDrawingCut = false;
        drawDessertTray();
    }
});

// Click serving slot bar area
document.getElementById("serving-tray-plate").addEventListener("click", () => {
    if (gameState.isScooped && gameState.servedSliceId !== null) {
        const slice = gameState.trayPolygons.find(p => p.id === gameState.servedSliceId);
        if (slice) {
            serveSliceToCustomer(slice.vertices);
        }
        
        // Reset tool image
        document.getElementById("fps-spatula-img").style.display = "none";
    }
});


// --- MENU NAVIGATIONS & UI CONTROLS ---

// Tool Switch click handlers
document.getElementById("tool-knife").addEventListener("click", () => {
    gameState.activeTool = 'knife';
    document.getElementById("tool-knife").className = "tool-btn active";
    document.getElementById("tool-spatula").className = "tool-btn";
    document.getElementById("fps-knife-img").style.display = "block";
    document.getElementById("fps-spatula-img").style.display = "none";
});

document.getElementById("tool-spatula").addEventListener("click", () => {
    gameState.activeTool = 'spatula';
    document.getElementById("tool-knife").className = "tool-btn";
    document.getElementById("tool-spatula").className = "tool-btn active";
    document.getElementById("fps-knife-img").style.display = "none";
    document.getElementById("fps-spatula-img").style.display = "block";
});

// Reset tray button
document.getElementById("tool-reset").addEventListener("click", () => {
    if (gameState.cash >= 2.00) {
        gameState.cash -= 2.00;
        gameState.expenses += 2.00;
        document.getElementById("hud-cash").innerText = `$${gameState.cash.toFixed(2)}`;
        
        // Clean
        resetDessertTray();
        audio.playScoop();
        
        // Reset scoop state if active
        gameState.isScooped = false;
        gameState.servedSliceId = null;
        document.getElementById("fps-spatula-img").style.display = "none";
        document.getElementById("serving-tray-plate").className = "";
    } else {
        // Can't afford
        audio.playFail();
        alert("Tepsiyi yenilemek için $2.00 kasanızda para bulunmalı!");
    }
});

// Sound control toggle
document.getElementById("toggle-sound-btn").addEventListener("click", () => {
    audio.init();
    const muted = audio.toggleMute();
    document.getElementById("sound-on-svg").style.display = muted ? "none" : "block";
    document.getElementById("sound-off-svg").style.display = muted ? "block" : "none";
});

// Start game triggers
document.getElementById("start-game-btn").addEventListener("click", () => {
    audio.init();
    document.getElementById("main-menu").className = "screen-overlay hidden";
    startDay(1);
});

document.getElementById("home-btn").addEventListener("click", () => {
    // Go to main menu
    document.getElementById("main-menu").className = "screen-overlay";
    document.getElementById("level-menu").className = "screen-overlay hidden";
    document.getElementById("how-to-menu").className = "screen-overlay hidden";
    document.getElementById("day-complete-panel").className = "screen-overlay hidden";
});

// Level select panels
document.getElementById("level-select-btn").addEventListener("click", () => {
    document.getElementById("level-menu").className = "screen-overlay";
});

document.getElementById("level-back-btn").addEventListener("click", () => {
    document.getElementById("level-menu").className = "screen-overlay hidden";
});

// How to play panel
document.getElementById("how-to-play-btn").addEventListener("click", () => {
    document.getElementById("how-to-menu").className = "screen-overlay";
});

document.getElementById("how-to-back-btn").addEventListener("click", () => {
    document.getElementById("how-to-menu").className = "screen-overlay hidden";
});

// Bind level click selectors
document.querySelectorAll(".level-card").forEach(card => {
    card.addEventListener("click", () => {
        const lvl = parseInt(card.getAttribute("data-level"));
        document.getElementById("level-menu").className = "screen-overlay hidden";
        document.getElementById("main-menu").className = "screen-overlay hidden";
        audio.init();
        startLevel(lvl);
    });
});

// Next Day button in report card
document.getElementById("next-day-btn").addEventListener("click", () => {
    document.getElementById("day-complete-panel").className = "screen-overlay hidden";
    
    // Move to next level / Day
    let nextLvl = gameState.currentLevel + 1;
    if (nextLvl > 3) nextLvl = 1; // Loop back
    
    gameState.currentDay++;
    startLevel(nextLvl);
});

// Main menu button in report card
document.getElementById("report-menu-btn").addEventListener("click", () => {
    document.getElementById("day-complete-panel").className = "screen-overlay hidden";
    document.getElementById("main-menu").className = "screen-overlay";
});


// --- GAME LEVEL STATE MANAGEMENT ---

function startLevel(lvl) {
    gameState.currentLevel = lvl;
    
    // Set level display name in instructions/dialogue initial Vibe
    const bubble = document.getElementById("dialogue-bubble");
    const text = document.getElementById("dialogue-text");
    const hint = document.getElementById("order-hint");
    
    let dessertName = "Karamelli Trileçe";
    if (lvl === 2) dessertName = "Hindistan Cevizli Revani";
    if (lvl === 3) dessertName = "Tepsi Fıstıklı Baklava";
    
    text.innerHTML = `<strong>Bölüm ${lvl}: ${dessertName} Tezgaha Geldi!</strong><br>Müşterileri beklemeye başla...`;
    hint.innerHTML = "Vitrin dükkanı açıldı!";
    bubble.className = "glass-panel active";
    
    // Clear old customer
    document.getElementById("customer-area").innerHTML = "";
    
    // Reset stats for current day
    gameState.customerIndex = 0;
    gameState.tipsEarned = 0;
    gameState.expenses = 0;
    gameState.dayAccuracySum = 0;
    gameState.dayAccuracyCount = 0;
    
    document.getElementById("hud-day").innerText = gameState.currentDay;
    
    // Reset Tray
    resetDessertTray();
    
    // Resize canvases
    resizeGlassCanvas();
    
    // Spawn first customer in queue after 3 seconds
    setTimeout(() => {
        spawnCustomer();
    }, 2800);
}

function startDay(dayNum) {
    gameState.currentDay = dayNum;
    startLevel(1); // Start from Level 1
}

// End of Day stats compiling
function endDayReport() {
    gameState.customerState = 'idle';
    
    const panel = document.getElementById("day-complete-panel");
    document.getElementById("report-day-title").innerText = `GÜN ${gameState.currentDay} BİTTİ!`;
    
    document.getElementById("stat-customers").innerText = `${gameState.customerMax} Müşteri`;
    
    let avgAcc = gameState.dayAccuracyCount > 0 ? Math.round(gameState.dayAccuracySum / gameState.dayAccuracyCount) : 0;
    document.getElementById("stat-accuracy").innerText = `%${avgAcc}`;
    
    document.getElementById("stat-tips").innerText = `$${gameState.tipsEarned.toFixed(2)}`;
    document.getElementById("stat-expenses").innerText = `$${gameState.expenses.toFixed(2)}`;
    
    // Net profit = customer base fee ($5/client) + tips - expenses
    let net = (gameState.customerMax * 5.00) + gameState.tipsEarned - gameState.expenses;
    document.getElementById("stat-net").innerText = `$${net.toFixed(2)}`;
    
    panel.className = "screen-overlay";
}

// Window resize listener
window.addEventListener("resize", () => {
    resizeGlassCanvas();
});

// Pre-init calls
resizeGlassCanvas();
drawDessertTray();
