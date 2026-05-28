'use client';

import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { useNexus } from '@/lib/store';

interface NodeData {
  lat: number;
  lng: number;
  kind: 'normal' | 'warning' | 'risk';
  label: string;
}

const NODE_DATA: NodeData[] = [
  { lat: -23,   lng: -46,   kind: 'risk',    label: 'SP-BR' },
  { lat:  40,   lng: -74,   kind: 'normal',  label: 'NYC'   },
  { lat:  51,   lng: -0.1,  kind: 'normal',  label: 'LDN'   },
  { lat:  35,   lng:  139,  kind: 'normal',  label: 'TYO'   },
  { lat: -33,   lng:  151,  kind: 'warning', label: 'SYD'   },
  { lat:   1,   lng:  103,  kind: 'normal',  label: 'SGP'   },
  { lat:  55,   lng:   37,  kind: 'normal',  label: 'MSK'   },
  { lat: -34,   lng:   18,  kind: 'warning', label: 'CPT'   },
  { lat:  28,   lng:   77,  kind: 'risk',    label: 'DEL'   },
  { lat: -15,   lng:  -47,  kind: 'normal',  label: 'BSB'   },
  { lat:  19,   lng:  -99,  kind: 'normal',  label: 'MEX'   },
  { lat:  60,   lng:   18,  kind: 'normal',  label: 'STO'   }
];

function latLngToVec3(lat: number, lng: number, r = 1.92): THREE.Vector3 {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lng + 180) * (Math.PI / 180);
  return new THREE.Vector3(
    -r * Math.sin(phi) * Math.cos(theta),
     r * Math.cos(phi),
     r * Math.sin(phi) * Math.sin(theta)
  );
}

export function WireframeGlobe() {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    const w = mount.clientWidth;
    const h = mount.clientHeight;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(35, w / h, 0.1, 100);
    camera.position.set(0, 0, 6.5);

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(w, h);
    mount.appendChild(renderer.domElement);

    const globeGroup = new THREE.Group();
    scene.add(globeGroup);

    // Dark inner sphere (depth)
    globeGroup.add(
      new THREE.Mesh(
        new THREE.SphereGeometry(1.9, 64, 64),
        new THREE.MeshBasicMaterial({ color: 0x0a0c10, transparent: true, opacity: 0.85 })
      )
    );

    // Latitude lines
    const latMat = new THREE.LineBasicMaterial({ color: 0x00f2ff, transparent: true, opacity: 0.18 });
    for (let i = 1; i < 12; i++) {
      const phi = (i / 12) * Math.PI;
      const r = Math.sin(phi) * 1.92;
      const y = Math.cos(phi) * 1.92;
      const pts: THREE.Vector3[] = [];
      for (let j = 0; j <= 64; j++) {
        const t = (j / 64) * Math.PI * 2;
        pts.push(new THREE.Vector3(Math.cos(t) * r, y, Math.sin(t) * r));
      }
      globeGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), latMat));
    }
    // Longitude lines
    const lonMat = new THREE.LineBasicMaterial({ color: 0x00f2ff, transparent: true, opacity: 0.14 });
    for (let i = 0; i < 12; i++) {
      const theta = (i / 12) * Math.PI * 2;
      const pts: THREE.Vector3[] = [];
      for (let j = 0; j <= 64; j++) {
        const phi = (j / 64) * Math.PI;
        const r = Math.sin(phi) * 1.92;
        pts.push(new THREE.Vector3(Math.cos(theta) * r, Math.cos(phi) * 1.92, Math.sin(theta) * r));
      }
      globeGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), lonMat));
    }

    // Atmospheric ring (reactive)
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x00f2ff, transparent: true, opacity: 0.35, side: THREE.DoubleSide
    });
    const ring = new THREE.Mesh(new THREE.RingGeometry(2.05, 2.08, 128), ringMat);
    ring.rotation.x = Math.PI / 2.3;
    scene.add(ring);

    const colorCyan    = new THREE.Color(0x00f2ff);
    const colorAmber   = new THREE.Color(0xffb800);
    const colorMagenta = new THREE.Color(0xff007a);
    const tmpColor     = new THREE.Color();

    // Geo nodes
    interface NodeRef {
      d: NodeData;
      halo: THREE.Mesh;
      core: THREE.Mesh;
      basePos: THREE.Vector3;
      seed: number;
    }
    const nodes: { group: THREE.Group; ref: NodeRef }[] = NODE_DATA.map((d) => {
      const pos = latLngToVec3(d.lat, d.lng, 1.94);
      const group = new THREE.Group();
      const core = new THREE.Mesh(
        new THREE.SphereGeometry(0.025, 12, 12),
        new THREE.MeshBasicMaterial({ color: 0xffffff })
      );
      const halo = new THREE.Mesh(
        new THREE.SphereGeometry(0.05, 16, 16),
        new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.25 })
      );
      group.add(core); group.add(halo);
      group.position.copy(pos); group.lookAt(0, 0, 0);
      globeGroup.add(group);
      return { group, ref: { d, halo, core, basePos: pos.clone(), seed: Math.random() * Math.PI * 2 } };
    });

    // Federated learning particles
    interface ParticleSystem {
      pts: THREE.Vector3[];
      dot: THREE.Mesh<THREE.BufferGeometry, THREE.MeshBasicMaterial>;
      t: number;
      baseSpeed: number;
    }
    const particleSystems: ParticleSystem[] = [];
    for (let i = 0; i < 8; i++) {
      const a = nodes[Math.floor(Math.random() * nodes.length)].ref.basePos;
      const b = nodes[Math.floor(Math.random() * nodes.length)].ref.basePos;
      if (a.equals(b)) continue;
      const mid = a.clone().add(b).multiplyScalar(0.5).normalize().multiplyScalar(2.6);
      const curve = new THREE.QuadraticBezierCurve3(a, mid, b);
      const pts = curve.getPoints(80);
      globeGroup.add(
        new THREE.Line(
          new THREE.BufferGeometry().setFromPoints(pts),
          new THREE.LineBasicMaterial({ color: 0x00f2ff, transparent: true, opacity: 0.07 })
        )
      );
      const dot = new THREE.Mesh(
        new THREE.SphereGeometry(0.022, 10, 10),
        new THREE.MeshBasicMaterial({ color: 0x00f2ff })
      );
      globeGroup.add(dot);
      particleSystems.push({ pts, dot, t: Math.random(), baseSpeed: 0.0025 + Math.random() * 0.003 });
    }

    // Stars background
    const starGeo = new THREE.BufferGeometry();
    const starPos = new Float32Array(240 * 3);
    for (let i = 0; i < 240; i++) {
      const r = 18 + Math.random() * 12;
      const t = Math.random() * Math.PI * 2;
      const p = Math.acos(2 * Math.random() - 1);
      starPos[i * 3]     = r * Math.sin(p) * Math.cos(t);
      starPos[i * 3 + 1] = r * Math.sin(p) * Math.sin(t);
      starPos[i * 3 + 2] = r * Math.cos(p);
    }
    starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
    const stars = new THREE.Points(
      starGeo,
      new THREE.PointsMaterial({ color: 0xffffff, size: 0.04, transparent: true, opacity: 0.55 })
    );
    scene.add(stars);

    // Animation loop: reads Zustand state every frame (no React re-renders).
    let frameId: number;
    const tick = (t: number) => {
      const s = useNexus.getState();
      const tempProgress = Math.max(0, Math.min(1, s.temperature / 3));
      const meshSpeedMul = 0.4 + (s.meshActivity / 100) * 1.4;
      const now = t / 1000;

      let fedBurst = 0;
      if (s.federationActive) {
        const dt = (performance.now() - s.federationStartedAt) / 1000;
        if (dt < 4) fedBurst = Math.max(0, 1 - dt / 4);
      }

      globeGroup.rotation.y += 0.0012 * (1 + fedBurst * 1.5);
      stars.rotation.y -= 0.0002;

      // Ring color
      tmpColor.copy(colorCyan).lerp(colorMagenta, tempProgress);
      if (fedBurst > 0) tmpColor.lerp(colorCyan, fedBurst);
      ring.material.color.copy(tmpColor);
      ring.material.opacity = 0.25 + 0.12 * Math.sin(now * 0.8) + tempProgress * 0.2 + fedBurst * 0.3;

      // Nodes
      nodes.forEach(({ ref }) => {
        const { d } = ref;
        let baseColor: THREE.Color;
        if (d.kind === 'risk') baseColor = colorMagenta;
        else if (d.kind === 'warning') baseColor = colorAmber;
        else baseColor = colorCyan;

        if (d.kind === 'normal' && tempProgress > 0.5) {
          tmpColor.copy(colorCyan).lerp(colorAmber, (tempProgress - 0.5) * 2);
        } else {
          tmpColor.copy(baseColor);
        }
        if (fedBurst > 0) tmpColor.lerp(colorCyan, fedBurst * 0.8);

        (ref.core.material as THREE.MeshBasicMaterial).color.copy(tmpColor);
        (ref.halo.material as THREE.MeshBasicMaterial).color.copy(tmpColor);

        const pulseSpeed = d.kind === 'risk' ? (1.8 + tempProgress * 2.5) : 1.4;
        const pulseAmp = d.kind === 'risk' ? (0.5 + tempProgress * 0.5) : 0.35;
        const s2 = 1 + pulseAmp * Math.sin(now * pulseSpeed + ref.seed) + fedBurst * 0.8;
        ref.halo.scale.setScalar(s2);
        (ref.halo.material as THREE.MeshBasicMaterial).opacity =
          0.35 - 0.18 * Math.sin(now * pulseSpeed + ref.seed) + fedBurst * 0.4;
      });

      // Particles
      particleSystems.forEach((p) => {
        p.t += p.baseSpeed * meshSpeedMul * (1 + fedBurst * 4);
        if (p.t >= 1) p.t = 0;
        const idx = Math.floor(p.t * (p.pts.length - 1));
        p.dot.position.copy(p.pts[idx]);
        tmpColor.copy(colorCyan);
        if (tempProgress > 0.5) tmpColor.lerp(colorAmber, (tempProgress - 0.5) * 1.5);
        p.dot.material.color.copy(tmpColor);
        p.dot.scale.setScalar(1 + fedBurst * 1.5);
      });

      renderer.render(scene, camera);
      frameId = requestAnimationFrame(tick);
    };
    frameId = requestAnimationFrame(tick);

    const onResize = () => {
      const W = mount.clientWidth;
      const H = mount.clientHeight;
      renderer.setSize(W, H);
      camera.aspect = W / H;
      camera.updateProjectionMatrix();
    };
    const ro = new ResizeObserver(onResize);
    ro.observe(mount);

    return () => {
      cancelAnimationFrame(frameId);
      ro.disconnect();
      renderer.dispose();
      if (renderer.domElement.parentNode === mount) mount.removeChild(renderer.domElement);
    };
  }, []);

  return <div ref={mountRef} className="absolute inset-0" />;
}
