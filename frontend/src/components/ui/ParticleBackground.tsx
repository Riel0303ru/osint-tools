import { useEffect, useRef } from 'react';
import { motion, useAnimationFrame } from 'framer-motion';

type Particle = {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  opacity: number;
  color: string;
};

type ParticleBackgroundProps = {
  particleCount?: number;
  className?: string;
  color?: 'cyan' | 'violet' | 'mixed';
  speed?: number;
  connectionDistance?: number;
};

export function ParticleBackground({
  particleCount = 50,
  className,
  color = 'cyan',
  speed = 0.5,
  connectionDistance = 150,
}: ParticleBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const mouseRef = useRef({ x: 0, y: 0, active: false });

  const colors = {
    cyan: '#00d4ff',
    violet: '#8b5cf6',
    mixed: '',
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Initialize particles
    particlesRef.current = Array.from({ length: particleCount }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * speed,
      vy: (Math.random() - 0.5) * speed,
      size: Math.random() * 2 + 1,
      opacity: Math.random() * 0.5 + 0.2,
      color: color === 'mixed'
        ? Math.random() > 0.5 ? colors.cyan : colors.violet
        : colors[color],
    }));

    const handleMouseMove = (e: MouseEvent) => {
      mouseRef.current = {
        x: e.clientX,
        y: e.clientY,
        active: true,
      };
    };

    const handleMouseLeave = () => {
      mouseRef.current.active = false;
    };

    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, [particleCount, color, speed]);

  useAnimationFrame(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const particles = particlesRef.current;

    particles.forEach((particle, i) => {
      // Update position
      particle.x += particle.vx;
      particle.y += particle.vy;

      // Bounce off edges
      if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1;
      if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1;

      // Keep within bounds
      particle.x = Math.max(0, Math.min(canvas.width, particle.x));
      particle.y = Math.max(0, Math.min(canvas.height, particle.y));

      // Mouse interaction
      if (mouseRef.current.active) {
        const dx = mouseRef.current.x - particle.x;
        const dy = mouseRef.current.y - particle.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 100) {
          particle.x -= dx * 0.02;
          particle.y -= dy * 0.02;
        }
      }

      // Draw particle
      ctx.beginPath();
      ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
      ctx.fillStyle = particle.color;
      ctx.globalAlpha = particle.opacity;
      ctx.fill();

      // Draw connections
      for (let j = i + 1; j < particles.length; j++) {
        const other = particles[j];
        const dx = other.x - particle.x;
        const dy = other.y - particle.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < connectionDistance) {
          ctx.beginPath();
          ctx.moveTo(particle.x, particle.y);
          ctx.lineTo(other.x, other.y);
          ctx.strokeStyle = particle.color;
          ctx.globalAlpha = (1 - dist / connectionDistance) * 0.2;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    });

    ctx.globalAlpha = 1;
  });

  return (
    <canvas
      ref={canvasRef}
      className={cn('fixed inset-0 pointer-events-none', className)}
      style={{ zIndex: 0 }}
    />
  );
}

function cn(...classNames: (string | boolean | undefined)[]) {
  return classNames.filter(Boolean).join(' ');
}

type CyberGridProps = {
  className?: string;
  opacity?: number;
};

export function CyberGrid({ className, opacity = 0.03 }: CyberGridProps) {
  return (
    <div
      className={cn('fixed inset-0 pointer-events-none', className)}
      style={{
        backgroundImage: `
          linear-gradient(rgba(0, 212, 255, ${opacity}) 1px, transparent 1px),
          linear-gradient(90deg, rgba(0, 212, 255, ${opacity}) 1px, transparent 1px)
        `,
        backgroundSize: '50px 50px',
        zIndex: 0,
      }}
    />
  );
}

type GradientOrbProps = {
  className?: string;
  color?: string;
  size?: number;
  blur?: number;
  animate?: boolean;
};

export function GradientOrb({
  className,
  color = 'rgba(0, 212, 255, 0.15)',
  size = 400,
  blur = 100,
  animate = true,
}: GradientOrbProps) {
  return (
    <motion.div
      className={cn('fixed rounded-full pointer-events-none', className)}
      style={{
        width: size,
        height: size,
        background: `radial-gradient(circle, ${color}, transparent)`,
        filter: `blur(${blur}px)`,
      }}
      animate={
        animate
          ? {
              scale: [1, 1.2, 1],
              opacity: [0.5, 0.8, 0.5],
            }
          : undefined
      }
      transition={{
        duration: 8,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
    />
  );
}

type AnimatedBackgroundProps = {
  className?: string;
  showParticles?: boolean;
  showGrid?: boolean;
  showOrbs?: boolean;
};

export function AnimatedBackground({
  className,
  showParticles = true,
  showGrid = true,
  showOrbs = true,
}: AnimatedBackgroundProps) {
  return (
    <div className={cn('fixed inset-0 overflow-hidden', className)}>
      {/* Gradient mesh */}
      <div
        className="absolute inset-0 bg-cyber-mesh"
        style={{ zIndex: 0 }}
      />

      {/* Grid */}
      {showGrid && <CyberGrid />}

      {/* Animated orbs */}
      {showOrbs && (
        <>
          <GradientOrb
            className="top-0 left-1/4 -translate-x-1/2 -translate-y-1/2"
            color="rgba(0, 212, 255, 0.08)"
            size={600}
          />
          <GradientOrb
            className="bottom-0 right-1/4 translate-x-1/2 translate-y-1/2"
            color="rgba(139, 92, 246, 0.06)"
            size={500}
          />
        </>
      )}

      {/* Particles */}
      {showParticles && (
        <ParticleBackground
          particleCount={30}
          color="mixed"
          speed={0.3}
          connectionDistance={120}
        />
      )}
    </div>
  );
}
