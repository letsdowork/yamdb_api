from rest_framework import serializers
from api.models import Categories, Genres, Titles, Reviews, Comments, User
from rest_framework.validators import UniqueValidator


class UsersSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=User.objects.all())])
    username = serializers.CharField(
        validators=[UniqueValidator(
            queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'bio', 'email', 'role')

    def create(self, validated_data):
        if validated_data['role'] == User.Roles.ADMIN:
            return User.objects.create(
                is_staff=True, is_superuser=True, **validated_data)
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        role = validated_data.get('role', None)
        if role == User.Roles.ADMIN:
            instance.is_staff = True
            instance.is_superuser = True
            instance.save()
            return instance
        instance.save()
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'bio', 'email', 'role')


class EmailRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(
        queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ('email',)


class TokenObtainSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    confirmation_code = serializers.CharField()

    class Meta:
        model = User
        fields = ('email', 'confirmation_code')


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Categories


class GenresSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Genres


class TitlesReadSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField(read_only=True)
    category = CategoriesSerializer(read_only=True)
    genre = GenresSerializer(read_only=True, many=True)

    class Meta:
        fields = '__all__'
        model = Titles


class TitlesWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Categories.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        many=True, slug_field='slug', queryset=Genres.objects.all())

    class Meta:
        fields = '__all__'
        model = Titles


class ReviewsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Reviews

    def create(self, validated_data):
        author = validated_data['author']
        title = validated_data['title']
        if Reviews.objects.filter(title_id=title, author=author).exists():
            raise serializers.ValidationError('review already exist')
        review = Reviews.objects.create(**validated_data)
        return review


class CommentsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comments
