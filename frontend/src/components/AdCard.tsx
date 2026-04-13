import { Link } from 'react-router-dom';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface AdCardProps {
  id: string;
  title: string;
  price: string;
  image: string;
}

export default function AdCard({ id, title, price, image }: AdCardProps) {
  return (
    <Link to={`/ads/${id}`} className="group">
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
        <div className="aspect-video w-full overflow-hidden bg-gray-100">
          <ImageWithFallback
            src={image}
            alt={title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        </div>
        <div className="p-4">
          <h3 className="text-gray-900 mb-1 line-clamp-1">{title}</h3>
          <p className="text-blue-600">{price}</p>
        </div>
      </div>
    </Link>
  );
}
