"use client";

import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { SimplexNoise } from "@/lib/noise";

function MorphSphere() {
  const meshRef = useRef<THREE.Mesh>(null);
  const noise = useMemo(() => new SimplexNoise(7), []);

  const geometry = useMemo(() => {
    const geo = new THREE.IcosahedronGeometry(1.6, 4);
    // stash the resting position of every vertex so we can displace
    // relative to it every frame instead of accumulating drift
    geo.userData.basePositions = geo.attributes.position.array.slice();
    return geo;
  }, []);

  useFrame(({ clock, pointer }) => {
    const mesh = meshRef.current;
    if (!mesh) return;

    const t = clock.getElapsedTime() * 0.28;
    const posAttr = mesh.geometry.attributes.position;
    const base = mesh.geometry.userData.basePositions as Float32Array;

    for (let i = 0; i < posAttr.count; i++) {
      const ix = i * 3;
      const bx = base[ix];
      const by = base[ix + 1];
      const bz = base[ix + 2];

      const n = noise.noise3D(bx * 0.9 + t, by * 0.9 + t, bz * 0.9 + t);
      const displacement = 1 + n * 0.16;

      posAttr.setXYZ(i, bx * displacement, by * displacement, bz * displacement);
    }
    posAttr.needsUpdate = true;
    mesh.geometry.computeVertexNormals();

    mesh.rotation.y = t * 0.6 + pointer.x * 0.15;
    mesh.rotation.x = t * 0.15 + pointer.y * 0.1;
  });

  return (
    <mesh ref={meshRef} geometry={geometry}>
      <meshBasicMaterial color="#4ade80" wireframe transparent opacity={0.85} />
    </mesh>
  );
}

function InnerGlow() {
  const ref = useRef<THREE.Mesh>(null);
  useFrame(({ clock }) => {
    if (!ref.current) return;
    const s = 1 + Math.sin(clock.getElapsedTime() * 0.6) * 0.02;
    ref.current.scale.set(s, s, s);
  });
  return (
    <mesh ref={ref}>
      <sphereGeometry args={[1.15, 32, 32]} />
      <meshBasicMaterial color="#0a0a0a" transparent opacity={0.55} />
    </mesh>
  );
}

export default function Scene() {
  return (
    <Canvas
      camera={{ position: [0, 0, 5], fov: 45 }}
      gl={{ antialias: true, alpha: true }}
      dpr={[1, 1.75]}
    >
      <ambientLight intensity={0.4} />
      <InnerGlow />
      <MorphSphere />
    </Canvas>
  );
}
