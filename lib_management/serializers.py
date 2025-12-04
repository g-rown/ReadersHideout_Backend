from rest_framework import serializers
from .models import Book, Category, Borrower, Borrowing


# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


# Book Serializer
class BookSerializer(serializers.ModelSerializer):
    shelf = serializers.IntegerField(required=False, min_value=1)
    row = serializers.IntegerField(required=False, min_value=1)
    column = serializers.IntegerField(required=False, min_value=1)

    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        required=False,
        source='category'
    )

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'isbn',
            'category', 'category_id', 'cover',
            'total_copies', 'available_copies', 'created_at',
            'shelf', 'row', 'column'
        ]
        read_only_fields = ['available_copies', 'created_at']

    # Create and Update Methods
    def create(self, validated_data):
        return Book.objects.create(**validated_data)

    def update(self, instance, validated_data):
        category = validated_data.pop('category', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if category:
            instance.category = category

        instance.save()
        return instance


# Borrower Serializer
class BorrowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrower
        fields = ['id', 'name', 'contact', 'email', 'address']



# Borrowing Serializer
class BorrowingSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        source='book',
        write_only=True
    )

    borrower = BorrowerSerializer(read_only=True)
    borrower_id = serializers.PrimaryKeyRelatedField(
        queryset=Borrower.objects.all(),
        source='borrower',
        write_only=True,
        required=False
    )

    borrower_name = serializers.CharField(write_only=True, required=False)
    borrower_contact = serializers.CharField(write_only=True, required=False)
    borrower_email = serializers.CharField(write_only=True, required=False)
    borrower_address = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Borrowing
        fields = [
            'id', 'book', 'book_id', 'borrower', 'borrower_id',
            'borrower_name', 'borrower_contact', 'borrower_email', 'borrower_address',
            'date_borrowed', 'date_due', 'date_returned', 'fine_amount'
        ]
        read_only_fields = ['date_borrowed', 'date_due', 'fine_amount']

    def create(self, validated_data):
        name = validated_data.pop('borrower_name', None)
        contact = validated_data.pop('borrower_contact', None)
        email = validated_data.pop('borrower_email', None)
        address = validated_data.pop('borrower_address', None)

        address = address if address else None

        if name:
            borrower, created = Borrower.objects.get_or_create(
                name=name,
                defaults={
                    'contact': contact, 
                    'email': email,     
                    'address': address
                }
            )
            validated_data['borrower'] = borrower

        if 'borrower' not in validated_data:
            raise serializers.ValidationError({"borrower_name": "Borrower Name or ID is required."})

        return super().create(validated_data)

    def update(self, instance, validated_data):
        allowed_fields = {'date_returned'}
        if set(validated_data.keys()) - allowed_fields:
            raise serializers.ValidationError("Only setting 'date_returned' is allowed for updates (the Return action).")
        
        if 'date_returned' in validated_data and instance.date_returned is None:
            instance.date_returned = validated_data['date_returned']
            instance.save()
            instance.refresh_from_db()

            return instance
        
        if instance.date_returned is not None:
            raise serializers.ValidationError("This book has already been returned.")

        return instance