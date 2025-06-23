import Link from 'next/link';
import { Video } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t">
      <div className="section-container py-12">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          <div className="col-span-2 md:col-span-1">
            <Link href="/" className="flex items-center gap-2">
              <Video className="h-6 w-6 text-blue-500" />
              <span className="text-lg font-bold">ManimGen</span>
            </Link>
            <p className="mt-4 text-sm text-gray-600">
              AI-powered educational animations.
            </p>
          </div>
          <div>
            <h3 className="font-semibold">Product</h3>
            <ul className="mt-4 space-y-2 text-sm">
              <li><Link href="/#features" className="text-gray-600 hover:text-gray-900">Features</Link></li>
              <li><Link href="/#generator" className="text-gray-600 hover:text-gray-900">Generator</Link></li>
              <li><Link href="#" className="text-gray-600 hover:text-gray-900">Pricing</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold">Company</h3>
            <ul className="mt-4 space-y-2 text-sm">
              <li><Link href="#" className="text-gray-600 hover:text-gray-900">About</Link></li>
              <li><Link href="#" className="text-gray-600 hover:text-gray-900">Blog</Link></li>
              <li><Link href="#" className="text-gray-600 hover:text-gray-900">Contact</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold">Legal</h3>
            <ul className="mt-4 space-y-2 text-sm">
              <li><Link href="#" className="text-gray-600 hover:text-gray-900">Privacy Policy</Link></li>
              <li><Link href="#" className="text-gray-600 hover:text-gray-900">Terms of Service</Link></li>
            </ul>
          </div>
        </div>
        <div className="mt-8 border-t pt-8 text-center text-sm text-gray-500">
          © {new Date().getFullYear()} ManimGen. All rights reserved.
        </div>
      </div>
    </footer>
  );
} 