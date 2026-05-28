import { Atmospherics } from '@/components/viewport/atmospherics';
import { TopBar } from '@/components/top-bar';
import { NexusDashboard } from '@/components/nexus-dashboard';
import { BottomDock } from '@/components/bottom-dock';
import { PredictionDrawer } from '@/components/modules/prediction-drawer';
import { BlockchainDrawer } from '@/components/modules/blockchain-drawer';
import { MeshDrawer } from '@/components/modules/mesh-drawer';
import { BriefingDrawer } from '@/components/modules/briefing-drawer';
import { Footer } from '@/components/ui/footer';

export default function Page() {
  return (
    <div className="relative min-h-screen nexus-bg-gradient overflow-hidden">
      <Atmospherics />
      <div className="absolute inset-0 nexus-noise opacity-50 pointer-events-none" />

      <main className="relative z-10 max-w-[1400px] mx-auto px-5 py-6 lg:px-8 lg:py-8">
        <TopBar />
        <NexusDashboard />
        <BottomDock />
        <Footer />
      </main>

      <PredictionDrawer />
      <BlockchainDrawer />
      <MeshDrawer />
      <BriefingDrawer />
    </div>
  );
}
