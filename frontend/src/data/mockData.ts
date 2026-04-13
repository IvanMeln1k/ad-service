export interface User {
  id: string;
  username: string;
  email: string;
  phone?: string;
  location?: string;
}

export const mockAds: Ad[] = [
  {
    id: '1',
    title: 'Modern Sofa - Like New',
    description: 'Beautiful modern sofa in excellent condition. Only 6 months old, selling due to relocation. Very comfortable and stylish, perfect for any living room. Dimensions: 200cm x 90cm x 85cm.',
    price: '$450',
    image: 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtb2Rlcm4lMjBmdXJuaXR1cmV8ZW58MXx8fHwxNzY0ODExMjU1fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
    category: 'furniture',
    userId: 'user1',
  },
  {
    id: '2',
    title: 'Vintage Film Camera',
    description: 'Classic vintage camera from the 1970s. Fully functional and well-maintained. Comes with original leather case and manual. Perfect for photography enthusiasts and collectors.',
    price: '$280',
    image: 'https://images.unsplash.com/photo-1495121553079-4c61bcce1894?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx2aW50YWdlJTIwY2FtZXJhfGVufDF8fHx8MTc2NDc3NDQxOXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
    category: 'electronics',
    userId: 'user2',
  },
  {
    id: '3',
    title: 'Mountain Bike - Excellent Condition',
    description: 'High-quality mountain bike, barely used. 21-speed gear system, aluminum frame, front suspension. Great for trails and city riding. Regularly serviced and maintained.',
    price: '$320',
    image: 'https://images.unsplash.com/photo-1485965120184-e220f721d03e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxiaWN5Y2xlfGVufDF8fHx8MTc2NDc0NjAwOXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
    category: 'sports',
    userId: 'user1',
  },
  {
    id: '4',
    title: 'MacBook Pro 2021',
    description: 'Apple MacBook Pro 14" with M1 Pro chip. 16GB RAM, 512GB SSD. Like new condition with original box and charger. Perfect for professionals and students.',
    price: '$1,400',
    image: 'https://images.unsplash.com/photo-1511385348-a52b4a160dc2?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxsYXB0b3AlMjBjb21wdXRlcnxlbnwxfHx8fDE3NjQ4MDgwNjZ8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
    category: 'electronics',
    userId: 'user3',
  },
  {
    id: '5',
    title: 'Honda Civic 2019',
    description: 'Well-maintained Honda Civic 2019. Only 35,000 miles. Excellent fuel economy, reliable and clean. Full service history available. Single owner.',
    price: '$18,500',
    image: 'https://images.unsplash.com/photo-1668764340793-06b6f00ea4d7?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjYXIlMjB2ZWhpY2xlfGVufDF8fHx8MTc2NDc1MjM3M3ww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
    category: 'vehicles',
    userId: 'user2',
  },
  {
    id: '6',
    title: 'Spacious Studio Apartment',
    description: 'Modern studio apartment for rent in downtown area. Fully furnished with all amenities. High-speed internet included. Great location near public transport and shopping.',
    price: '$950/month',
    image: 'https://images.unsplash.com/photo-1675279200694-8529c73b1fd0?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhcGFydG1lbnQlMjBpbnRlcmlvcnxlbnwxfHx8fDE3NjQ4MTkzNDV8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
    category: 'real-estate',
    userId: 'user1',
  },
];

export const currentUser: User = {
  id: 'user1',
  username: 'johndoe',
  email: 'john@example.com',
  phone: '+1 (555) 123-4567',
  location: 'New York, NY',
};

export const mockUsers: User[] = [
  {
    id: 'user1',
    username: 'johndoe',
    email: 'john@example.com',
    phone: '+1 (555) 123-4567',
    location: 'New York, NY',
  },
  {
    id: 'user2',
    username: 'sarahsmith',
    email: 'sarah.smith@example.com',
    phone: '+1 (555) 234-5678',
    location: 'Los Angeles, CA',
  },
  {
    id: 'user3',
    username: 'mikechen',
    email: 'mike.chen@example.com',
    phone: '+1 (555) 345-6789',
    location: 'San Francisco, CA',
  },
];