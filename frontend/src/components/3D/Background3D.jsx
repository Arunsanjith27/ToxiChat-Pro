import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Sphere, Stars } from '@react-three/drei';
import * as THREE from 'three';

function FloatingSpheres() {
  const groupRef = useRef();

  useFrame((state) => {
    groupRef.current.rotation.y += 0.001;
    groupRef.current.rotation.x += 0.0005;
  });

  // Generate deterministic random positions
  const spheres = useMemo(() => {
    return Array.from({ length: 15 }).map((_, i) => ({
      position: [
        (Math.random() - 0.5) * 20,
        (Math.random() - 0.5) * 20,
        (Math.random() - 0.5) * 15 - 5,
      ],
      scale: Math.random() * 0.5 + 0.1,
      color: i % 3 === 0 ? '#10b981' : i % 3 === 1 ? '#3b82f6' : '#8b5cf6',
    }));
  }, []);

  return (
    <group ref={groupRef}>
      {spheres.map((s, i) => (
        <Float key={i} speed={2} rotationIntensity={1} floatIntensity={2}>
          <Sphere args={[s.scale, 32, 32]} position={s.position}>
            <meshStandardMaterial
              color={s.color}
              emissive={s.color}
              emissiveIntensity={0.2}
              roughness={0.2}
              metalness={0.8}
              transparent
              opacity={0.4}
            />
          </Sphere>
        </Float>
      ))}
    </group>
  );
}

export default function Background3D() {
  return (
    <div className="fixed inset-0 z-[-1] bg-gradient-to-b from-space-bg to-black">
      <Canvas camera={{ position: [0, 0, 10], fov: 60 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} color="#ffffff" />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="#10b981" />
        
        <Stars radius={100} depth={50} count={3000} factor={4} saturation={0} fade speed={1} />
        <FloatingSpheres />
        
        <fog attach="fog" args={['#0b0f19', 10, 30]} />
      </Canvas>
    </div>
  );
}
