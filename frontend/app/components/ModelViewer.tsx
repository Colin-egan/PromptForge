"use client";

import { Suspense, useEffect, useRef } from "react";
import { Canvas, useThree } from "@react-three/fiber";
import { OrbitControls, Environment, Center } from "@react-three/drei";
import { useLoader } from "@react-three/fiber";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import * as THREE from "three";
import { modelGlbUrl } from "../lib/api";

function Model({ url }: { url: string }) {
  const gltf = useLoader(GLTFLoader, url);

  // Center and scale model to fit viewport
  const boxRef = useRef(new THREE.Box3());
  useEffect(() => {
    boxRef.current.setFromObject(gltf.scene);
    const size = new THREE.Vector3();
    boxRef.current.getSize(size);
    const maxDim = Math.max(size.x, size.y, size.z);
    if (maxDim > 0) {
      const scale = 4 / maxDim;
      gltf.scene.scale.setScalar(scale);
    }
    const center = new THREE.Vector3();
    boxRef.current.setFromObject(gltf.scene).getCenter(center);
    gltf.scene.position.sub(center);
  }, [gltf]);

  return <primitive object={gltf.scene} />;
}

function CameraSetup() {
  const { camera } = useThree();
  useEffect(() => {
    camera.position.set(5, 5, 8);
    camera.lookAt(0, 0, 0);
  }, [camera]);
  return null;
}

interface ModelViewerProps {
  modelId: string | null;
}

export default function ModelViewer({ modelId }: ModelViewerProps) {
  if (!modelId) {
    return (
      <div className="flex items-center justify-center h-full" style={{ background: "var(--bg)" }}>
        <div className="text-center" style={{ color: "var(--muted)" }}>
          <div className="text-6xl mb-4">⬡</div>
          <p className="text-sm">Your 3D model will appear here</p>
          <p className="text-xs mt-1 opacity-60">Describe an object in the chat to get started</p>
        </div>
      </div>
    );
  }

  const glbUrl = modelGlbUrl(modelId);

  return (
    <div className="h-full w-full" style={{ background: "var(--bg)" }}>
      <Canvas shadows>
        <CameraSetup />
        <ambientLight intensity={0.6} />
        <directionalLight position={[10, 10, 5]} intensity={1.2} castShadow />
        <directionalLight position={[-5, -5, -5]} intensity={0.3} />
        <Suspense
          fallback={
            <mesh>
              <boxGeometry args={[1, 1, 1]} />
              <meshStandardMaterial color="#6366f1" wireframe />
            </mesh>
          }
        >
          <Center>
            <Model url={glbUrl} />
          </Center>
        </Suspense>
        <OrbitControls makeDefault enableDamping dampingFactor={0.05} />
        <gridHelper args={[20, 20, "#2d2d42", "#2d2d42"]} />
      </Canvas>
    </div>
  );
}
